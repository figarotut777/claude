"""
Utility functions for notifications, logging, and helpers.
"""
import asyncio
import random
from datetime import datetime
from typing import Optional
import httpx
from models import LogEntry, TimeSlot


class TelegramNotifier:
    """
    Telegram notification handler.

    Sends alerts via Telegram Bot API.
    """

    BASE_URL = "https://api.telegram.org"

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Initialize Telegram notifier.

        Args:
            bot_token: Telegram bot token from @BotFather
            chat_id: Telegram chat ID to send messages to
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.enabled = bool(bot_token and chat_id)

    async def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send a message via Telegram.

        Args:
            message: Message text (supports HTML or Markdown)
            parse_mode: Message formatting (HTML or Markdown)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            return False

        try:
            url = f"{self.BASE_URL}/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode,
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)

                if response.status_code == 200:
                    return True
                else:
                    print(f"Telegram API error: {response.text}")
                    return False

        except Exception as e:
            print(f"Failed to send Telegram notification: {str(e)}")
            return False

    async def notify_slot_found(self, slot: TimeSlot, warehouse_name: str) -> bool:
        """
        Send notification about found slot.

        Args:
            slot: TimeSlot object
            warehouse_name: Name of the warehouse

        Returns:
            True if sent successfully
        """
        message = (
            f"🎯 <b>Slot Found!</b>\n\n"
            f"📍 <b>Warehouse:</b> {warehouse_name}\n"
            f"📅 <b>Date:</b> {slot.date}\n"
            f"🕐 <b>Time:</b> {slot.time}\n"
            f"📊 <b>Coefficient:</b> {slot.coefficient}x\n"
            f"📦 <b>Quota:</b> {slot.quota}\n\n"
            f"🔔 Action required!"
        )
        return await self.send_message(message)

    async def notify_booking_success(
        self,
        slot: TimeSlot,
        warehouse_name: str,
        booking_id: Optional[str] = None
    ) -> bool:
        """
        Send notification about successful booking.

        Args:
            slot: TimeSlot object
            warehouse_name: Name of the warehouse
            booking_id: Booking confirmation ID

        Returns:
            True if sent successfully
        """
        message = (
            f"✅ <b>Booking Successful!</b>\n\n"
            f"📍 <b>Warehouse:</b> {warehouse_name}\n"
            f"📅 <b>Date:</b> {slot.date}\n"
            f"🕐 <b>Time:</b> {slot.time}\n"
            f"📊 <b>Coefficient:</b> {slot.coefficient}x\n"
        )

        if booking_id:
            message += f"🆔 <b>Booking ID:</b> {booking_id}\n"

        message += f"\n🎉 Slot has been auto-booked!"

        return await self.send_message(message)

    async def notify_booking_failed(
        self,
        slot: TimeSlot,
        warehouse_name: str,
        error: str
    ) -> bool:
        """
        Send notification about failed booking.

        Args:
            slot: TimeSlot object
            warehouse_name: Name of the warehouse
            error: Error message

        Returns:
            True if sent successfully
        """
        message = (
            f"❌ <b>Booking Failed!</b>\n\n"
            f"📍 <b>Warehouse:</b> {warehouse_name}\n"
            f"📅 <b>Date:</b> {slot.date}\n"
            f"🕐 <b>Time:</b> {slot.time}\n"
            f"📊 <b>Coefficient:</b> {slot.coefficient}x\n\n"
            f"⚠️ <b>Error:</b> {error}"
        )
        return await self.send_message(message)

    async def notify_error(self, error_message: str) -> bool:
        """
        Send error notification.

        Args:
            error_message: Error description

        Returns:
            True if sent successfully
        """
        message = f"⚠️ <b>Error</b>\n\n{error_message}"
        return await self.send_message(message)

    async def test_connection(self) -> tuple[bool, str]:
        """
        Test Telegram bot connection.

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.enabled:
            return False, "Telegram notifications not configured"

        try:
            url = f"{self.BASE_URL}/bot{self.bot_token}/getMe"

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)

                if response.status_code == 200:
                    data = response.json()
                    bot_name = data.get("result", {}).get("username", "Unknown")
                    return True, f"Connected to bot: @{bot_name}"
                else:
                    return False, f"Connection failed: {response.text}"

        except Exception as e:
            return False, f"Connection failed: {str(e)}"


class Logger:
    """
    In-memory logger for the dashboard.

    Stores logs in a list with automatic size management.
    """

    def __init__(self, max_logs: int = 1000):
        """
        Initialize logger.

        Args:
            max_logs: Maximum number of logs to keep in memory
        """
        self.max_logs = max_logs
        self.logs: list[LogEntry] = []

    def log(
        self,
        message: str,
        level: str = "INFO",
        task_id: Optional[str] = None
    ) -> LogEntry:
        """
        Add a log entry.

        Args:
            message: Log message
            level: Log level (INFO, SUCCESS, WARNING, ERROR)
            task_id: Associated task ID

        Returns:
            Created LogEntry
        """
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            message=message,
            task_id=task_id,
        )

        self.logs.append(entry)

        # Keep only the most recent logs
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]

        return entry

    def info(self, message: str, task_id: Optional[str] = None) -> LogEntry:
        """Log INFO level message."""
        return self.log(message, "INFO", task_id)

    def success(self, message: str, task_id: Optional[str] = None) -> LogEntry:
        """Log SUCCESS level message."""
        return self.log(message, "SUCCESS", task_id)

    def warning(self, message: str, task_id: Optional[str] = None) -> LogEntry:
        """Log WARNING level message."""
        return self.log(message, "WARNING", task_id)

    def error(self, message: str, task_id: Optional[str] = None) -> LogEntry:
        """Log ERROR level message."""
        return self.log(message, "ERROR", task_id)

    def get_recent_logs(self, count: int = 100, task_id: Optional[str] = None) -> list[LogEntry]:
        """
        Get recent log entries.

        Args:
            count: Number of logs to retrieve
            task_id: Filter by task ID (optional)

        Returns:
            List of LogEntry objects
        """
        logs = self.logs

        if task_id:
            logs = [log for log in logs if log.task_id == task_id]

        return logs[-count:]

    def clear(self):
        """Clear all logs."""
        self.logs = []


async def random_delay(min_seconds: float = 30.0, max_seconds: float = 60.0):
    """
    Sleep for a random duration to avoid rate limiting.

    Args:
        min_seconds: Minimum delay in seconds
        max_seconds: Maximum delay in seconds
    """
    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)


def format_coefficient(coefficient: float) -> str:
    """
    Format coefficient for display.

    Args:
        coefficient: Raw coefficient value

    Returns:
        Formatted string (e.g., "x1.5", "x10")
    """
    return f"x{coefficient:.1f}" if coefficient < 10 else f"x{int(coefficient)}"


def get_date_range_str(start_date, end_date) -> str:
    """
    Format date range for display.

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        Formatted string
    """
    if start_date == end_date:
        return start_date.strftime("%Y-%m-%d")
    return f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"


# Example usage
async def example_telegram_usage():
    """Example Telegram notification usage."""
    notifier = TelegramNotifier(
        bot_token="YOUR_BOT_TOKEN",
        chat_id="YOUR_CHAT_ID"
    )

    # Test connection
    success, message = await notifier.test_connection()
    print(f"Telegram test: {message}")

    if success:
        # Send test message
        await notifier.send_message("🚀 <b>WB Slot Monitor</b> is now active!")


if __name__ == "__main__":
    asyncio.run(example_telegram_usage())
