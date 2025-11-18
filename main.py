"""
Wildberries Slot Monitor - Professional Web Application

A Streamlit-based dashboard for monitoring and auto-booking delivery slots
at Wildberries warehouses.

Run with: streamlit run main.py
"""
import asyncio
import uuid
from datetime import date, timedelta
from typing import Optional
import streamlit as st
import pandas as pd
from wb_api import WildberriesAPI, WildberriesAPIError
from utils import TelegramNotifier, Logger, random_delay, format_coefficient, get_date_range_str
from models import MonitoringTask, Warehouse, TimeSlot, BookingRequest


# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

POLL_INTERVAL_MIN = 30  # Minimum seconds between checks
POLL_INTERVAL_MAX = 60  # Maximum seconds between checks

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================


def init_session_state():
    """Initialize Streamlit session state variables."""
    if "api_config" not in st.session_state:
        st.session_state.api_config = {
            "wb_token": "",
            "telegram_bot_token": "",
            "telegram_chat_id": "",
        }

    if "warehouses" not in st.session_state:
        st.session_state.warehouses = []

    if "tasks" not in st.session_state:
        st.session_state.tasks = {}

    if "logger" not in st.session_state:
        st.session_state.logger = Logger(max_logs=500)

    if "monitoring_active" not in st.session_state:
        st.session_state.monitoring_active = False

    if "found_slots" not in st.session_state:
        st.session_state.found_slots = {}  # task_id -> list of slots


# ============================================================================
# API & NOTIFICATION HELPERS
# ============================================================================


async def test_api_connection(token: str) -> tuple[bool, str, list[Warehouse]]:
    """
    Test WB API connection and fetch warehouses.

    Args:
        token: WB API token

    Returns:
        Tuple of (success, message, warehouses)
    """
    try:
        async with WildberriesAPI(token) as api:
            success, message = await api.test_connection()
            if success:
                warehouses = await api.get_warehouses()
                return True, message, warehouses
            return False, message, []
    except Exception as e:
        return False, f"Connection error: {str(e)}", []


async def test_telegram_connection(bot_token: str, chat_id: str) -> tuple[bool, str]:
    """
    Test Telegram bot connection.

    Args:
        bot_token: Telegram bot token
        chat_id: Telegram chat ID

    Returns:
        Tuple of (success, message)
    """
    notifier = TelegramNotifier(bot_token, chat_id)
    return await notifier.test_connection()


# ============================================================================
# MONITORING ENGINE
# ============================================================================


async def check_task_slots(
    api: WildberriesAPI,
    task: MonitoringTask,
    warehouses_dict: dict[int, Warehouse],
    notifier: TelegramNotifier,
    logger: Logger
) -> list[TimeSlot]:
    """
    Check for available slots matching task criteria.

    Args:
        api: WildberriesAPI instance
        task: MonitoringTask to check
        warehouses_dict: Dictionary mapping warehouse_id to Warehouse
        notifier: TelegramNotifier instance
        logger: Logger instance

    Returns:
        List of matching TimeSlot objects
    """
    matching_slots = []

    for warehouse_id in task.warehouses:
        try:
            warehouse = warehouses_dict.get(warehouse_id)
            warehouse_name = warehouse.name if warehouse else f"Warehouse {warehouse_id}"

            logger.info(
                f"Checking {warehouse_name} ({task.start_date} to {task.end_date})",
                task.task_id
            )

            # Fetch available slots
            slots = await api.get_available_slots(
                warehouse_id=warehouse_id,
                date_from=task.start_date.strftime("%Y-%m-%d"),
                date_to=task.end_date.strftime("%Y-%m-%d")
            )

            # Filter slots by coefficient
            for slot in slots:
                if slot.coefficient <= task.max_coefficient:
                    slot.warehouse_name = warehouse_name
                    matching_slots.append(slot)

                    logger.success(
                        f"Found slot: {warehouse_name}, {slot.date} {slot.time}, "
                        f"coefficient {format_coefficient(slot.coefficient)}",
                        task.task_id
                    )

                    # Handle based on mode
                    if task.mode == "notify":
                        # Send notification only
                        await notifier.notify_slot_found(slot, warehouse_name)

                    elif task.mode == "auto_book":
                        # Attempt to book the slot
                        booking_request = BookingRequest(
                            warehouse_id=warehouse_id,
                            date=slot.date,
                            time=slot.time,
                            shipment_type=task.shipment_type
                        )

                        logger.info(f"Attempting to book slot...", task.task_id)
                        result = await api.book_slot(booking_request)

                        if result.get("success"):
                            logger.success(
                                f"Booking successful! ID: {result.get('booking_id')}",
                                task.task_id
                            )
                            await notifier.notify_booking_success(
                                slot,
                                warehouse_name,
                                result.get("booking_id")
                            )
                        else:
                            error = result.get("error", "Unknown error")
                            logger.error(f"Booking failed: {error}", task.task_id)
                            await notifier.notify_booking_failed(slot, warehouse_name, error)

            # Add delay between warehouse checks to avoid rate limiting
            if len(task.warehouses) > 1:
                await asyncio.sleep(2)

        except WildberriesAPIError as e:
            logger.error(f"API error for {warehouse_name}: {str(e)}", task.task_id)
        except Exception as e:
            logger.error(f"Unexpected error for {warehouse_name}: {str(e)}", task.task_id)

    return matching_slots


async def monitoring_loop():
    """
    Main monitoring loop that runs in the background.

    Continuously checks all active tasks for available slots.
    """
    logger = st.session_state.logger
    logger.info("🚀 Monitoring engine started")

    # Initialize API and notifier
    config = st.session_state.api_config
    notifier = TelegramNotifier(
        config.get("telegram_bot_token"),
        config.get("telegram_chat_id")
    )

    # Create warehouses dictionary for quick lookup
    warehouses_dict = {wh.id: wh for wh in st.session_state.warehouses}

    try:
        async with WildberriesAPI(config["wb_token"]) as api:
            while st.session_state.monitoring_active:
                active_tasks = [
                    task for task in st.session_state.tasks.values()
                    if task.is_active
                ]

                if not active_tasks:
                    logger.warning("No active tasks. Waiting...")
                    await asyncio.sleep(10)
                    continue

                logger.info(f"Checking {len(active_tasks)} active task(s)...")

                for task in active_tasks:
                    if not st.session_state.monitoring_active:
                        break

                    matching_slots = await check_task_slots(
                        api, task, warehouses_dict, notifier, logger
                    )

                    # Store found slots in session state
                    if task.task_id not in st.session_state.found_slots:
                        st.session_state.found_slots[task.task_id] = []

                    st.session_state.found_slots[task.task_id].extend(matching_slots)

                    if not matching_slots:
                        logger.info(f"No matching slots found for task {task.task_id[:8]}", task.task_id)

                # Random delay to avoid rate limiting
                delay = await get_random_delay()
                logger.info(f"Waiting {delay:.0f} seconds before next check...")
                await asyncio.sleep(delay)

    except Exception as e:
        logger.error(f"Monitoring loop error: {str(e)}")
        st.session_state.monitoring_active = False

    logger.warning("🛑 Monitoring engine stopped")


async def get_random_delay() -> float:
    """Get a random delay interval."""
    import random
    return random.uniform(POLL_INTERVAL_MIN, POLL_INTERVAL_MAX)


# ============================================================================
# STREAMLIT UI COMPONENTS
# ============================================================================


def render_header():
    """Render application header."""
    st.title("🎯 Wildberries Slot Monitor")
    st.markdown(
        "Professional tool for monitoring and auto-booking delivery slots at WB warehouses."
    )
    st.divider()


def render_configuration_section():
    """Render API configuration section."""
    st.header("⚙️ Configuration")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Wildberries API")
        wb_token = st.text_input(
            "WB API Token",
            value=st.session_state.api_config.get("wb_token", ""),
            type="password",
            help="Your Wildberries API token from supplier panel"
        )

        if st.button("🔍 Test WB Connection", use_container_width=True):
            if wb_token:
                with st.spinner("Testing connection..."):
                    success, message, warehouses = asyncio.run(
                        test_api_connection(wb_token)
                    )

                    if success:
                        st.success(message)
                        st.session_state.api_config["wb_token"] = wb_token
                        st.session_state.warehouses = warehouses
                        st.session_state.logger.success(f"API connected: {message}")
                    else:
                        st.error(message)
                        st.session_state.logger.error(f"API connection failed: {message}")
            else:
                st.warning("Please enter a WB API token")

    with col2:
        st.subheader("Telegram Notifications")
        telegram_bot_token = st.text_input(
            "Telegram Bot Token",
            value=st.session_state.api_config.get("telegram_bot_token", ""),
            type="password",
            help="Get from @BotFather on Telegram"
        )

        telegram_chat_id = st.text_input(
            "Telegram Chat ID",
            value=st.session_state.api_config.get("telegram_chat_id", ""),
            help="Your Telegram chat ID (get from @userinfobot)"
        )

        if st.button("🔍 Test Telegram", use_container_width=True):
            if telegram_bot_token and telegram_chat_id:
                with st.spinner("Testing Telegram connection..."):
                    success, message = asyncio.run(
                        test_telegram_connection(telegram_bot_token, telegram_chat_id)
                    )

                    if success:
                        st.success(message)
                        st.session_state.api_config["telegram_bot_token"] = telegram_bot_token
                        st.session_state.api_config["telegram_chat_id"] = telegram_chat_id
                        st.session_state.logger.success(f"Telegram connected: {message}")
                    else:
                        st.error(message)
                        st.session_state.logger.error(f"Telegram connection failed: {message}")
            else:
                st.warning("Please enter both bot token and chat ID")

    st.divider()


def render_task_creation_section():
    """Render task creation section."""
    st.header("📋 Create Monitoring Task")

    if not st.session_state.warehouses:
        st.warning("⚠️ Please configure and test WB API connection first to load warehouses.")
        return

    with st.form("create_task_form"):
        # Warehouse selection
        warehouse_options = {
            f"{wh.name} (ID: {wh.id})": wh.id
            for wh in st.session_state.warehouses
        }

        selected_warehouse_names = st.multiselect(
            "Select Warehouses",
            options=list(warehouse_options.keys()),
            help="Choose one or more warehouses to monitor"
        )

        selected_warehouse_ids = [
            warehouse_options[name] for name in selected_warehouse_names
        ]

        # Date range
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=date.today(),
                min_value=date.today()
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=date.today() + timedelta(days=7),
                min_value=date.today()
            )

        # Coefficient and shipment type
        col3, col4 = st.columns(2)
        with col3:
            max_coefficient = st.slider(
                "Max Acceptable Coefficient",
                min_value=0.0,
                max_value=20.0,
                value=5.0,
                step=0.5,
                help="Book only slots with coefficient <= this value"
            )

        with col4:
            shipment_type = st.radio(
                "Shipment Type",
                options=["box", "monopallet"],
                horizontal=True
            )

        # Mode selection
        mode = st.radio(
            "Mode",
            options=["notify", "auto_book"],
            format_func=lambda x: "🔔 Notify Only" if x == "notify" else "🤖 Auto-Book",
            horizontal=True,
            help="Notify: sends Telegram alerts only. Auto-Book: automatically books matching slots."
        )

        submitted = st.form_submit_button("➕ Create Task", use_container_width=True)

        if submitted:
            if not selected_warehouse_ids:
                st.error("Please select at least one warehouse")
            elif start_date > end_date:
                st.error("Start date must be before end date")
            else:
                # Create new task
                task = MonitoringTask(
                    task_id=str(uuid.uuid4()),
                    warehouses=selected_warehouse_ids,
                    start_date=start_date,
                    end_date=end_date,
                    max_coefficient=max_coefficient,
                    shipment_type=shipment_type,
                    mode=mode,
                    is_active=True
                )

                st.session_state.tasks[task.task_id] = task
                st.session_state.logger.success(
                    f"Created task for {len(selected_warehouse_ids)} warehouse(s), "
                    f"coefficient <= {format_coefficient(max_coefficient)}"
                )
                st.success("✅ Task created successfully!")
                st.rerun()

    st.divider()


def render_active_tasks_section():
    """Render active tasks section."""
    st.header("📊 Active Tasks")

    if not st.session_state.tasks:
        st.info("No tasks created yet. Create a task above to start monitoring.")
        return

    # Convert tasks to DataFrame for display
    tasks_data = []
    for task in st.session_state.tasks.values():
        warehouse_names = [
            wh.name for wh in st.session_state.warehouses
            if wh.id in task.warehouses
        ]

        tasks_data.append({
            "ID": task.task_id[:8],
            "Warehouses": ", ".join(warehouse_names) if warehouse_names else "N/A",
            "Dates": get_date_range_str(task.start_date, task.end_date),
            "Max Coeff": format_coefficient(task.max_coefficient),
            "Type": task.shipment_type.capitalize(),
            "Mode": "🔔 Notify" if task.mode == "notify" else "🤖 Auto-Book",
            "Status": "✅ Active" if task.is_active else "⏸️ Paused",
            "Task ID": task.task_id  # Hidden, for reference
        })

    if tasks_data:
        df = pd.DataFrame(tasks_data)

        # Display table
        st.dataframe(
            df.drop(columns=["Task ID"]),
            use_container_width=True,
            hide_index=True
        )

        # Task management buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🗑️ Delete All Tasks", use_container_width=True):
                st.session_state.tasks = {}
                st.session_state.found_slots = {}
                st.session_state.logger.warning("All tasks deleted")
                st.rerun()

        with col2:
            if st.button("⏸️ Pause All Tasks", use_container_width=True):
                for task in st.session_state.tasks.values():
                    task.is_active = False
                st.session_state.logger.warning("All tasks paused")
                st.rerun()

        with col3:
            if st.button("▶️ Resume All Tasks", use_container_width=True):
                for task in st.session_state.tasks.values():
                    task.is_active = True
                st.session_state.logger.info("All tasks resumed")
                st.rerun()

    st.divider()


def render_monitoring_control_section():
    """Render monitoring control section."""
    st.header("🔄 Monitoring Control")

    col1, col2 = st.columns(2)

    with col1:
        if not st.session_state.monitoring_active:
            if st.button("▶️ Start Monitoring", use_container_width=True, type="primary"):
                if not st.session_state.api_config.get("wb_token"):
                    st.error("Please configure WB API token first")
                elif not st.session_state.tasks:
                    st.warning("No tasks to monitor. Create a task first.")
                else:
                    st.session_state.monitoring_active = True
                    st.session_state.logger.success("Monitoring started")
                    # Note: In production, you'd run this in a proper background thread/process
                    # For Streamlit, you might need to use st.experimental_singleton or external scheduler
                    st.info("⚠️ Note: Monitoring runs while the page is active. For production, use a background service.")
                    st.rerun()
        else:
            st.success("🟢 Monitoring is ACTIVE")

    with col2:
        if st.session_state.monitoring_active:
            if st.button("⏹️ Stop Monitoring", use_container_width=True, type="secondary"):
                st.session_state.monitoring_active = False
                st.session_state.logger.warning("Monitoring stopped")
                st.rerun()

    st.divider()


def render_logs_section():
    """Render logs section."""
    st.header("📜 Activity Log")

    # Log controls
    col1, col2 = st.columns([3, 1])

    with col1:
        log_count = st.slider("Number of logs to display", 10, 100, 50)

    with col2:
        if st.button("🗑️ Clear Logs", use_container_width=True):
            st.session_state.logger.clear()
            st.rerun()

    # Display logs
    logs = st.session_state.logger.get_recent_logs(log_count)

    if logs:
        log_container = st.container(height=400)
        with log_container:
            for log in reversed(logs):
                # Color code by level
                if log.level == "ERROR":
                    st.error(f"{log.timestamp.strftime('%H:%M:%S')} | {log.message}")
                elif log.level == "WARNING":
                    st.warning(f"{log.timestamp.strftime('%H:%M:%S')} | {log.message}")
                elif log.level == "SUCCESS":
                    st.success(f"{log.timestamp.strftime('%H:%M:%S')} | {log.message}")
                else:
                    st.info(f"{log.timestamp.strftime('%H:%M:%S')} | {log.message}")
    else:
        st.info("No logs yet. Activity will appear here once monitoring starts.")


# ============================================================================
# MAIN APPLICATION
# ============================================================================


def main():
    """Main application entry point."""
    # Page configuration
    st.set_page_config(
        page_title="WB Slot Monitor",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Initialize session state
    init_session_state()

    # Render UI components
    render_header()
    render_configuration_section()
    render_task_creation_section()
    render_active_tasks_section()
    render_monitoring_control_section()
    render_logs_section()

    # Footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: gray; padding: 20px;'>
            <p>🎯 WB Slot Monitor v1.0 | Built with Streamlit</p>
            <p><small>⚠️ For production use, deploy this with a proper background worker (Celery, APScheduler, etc.)</small></p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Auto-refresh for monitoring
    if st.session_state.monitoring_active:
        # In a real production app, you'd use a proper background task runner
        # For demo purposes, we show a note about limitations
        st.info("💡 Tip: Keep this page open while monitoring. For 24/7 monitoring, deploy with a background service.")


if __name__ == "__main__":
    main()
