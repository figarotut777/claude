"""
Pydantic models for data validation and type safety.
"""
from datetime import date, datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, validator


class Warehouse(BaseModel):
    """Warehouse information from WB API."""
    id: int
    name: str
    address: Optional[str] = None


class TimeSlot(BaseModel):
    """Available time slot for delivery."""
    date: str
    time: str
    coefficient: float
    quota: int = Field(default=0, description="Available quota")
    warehouse_id: int
    warehouse_name: Optional[str] = None


class MonitoringTask(BaseModel):
    """Configuration for a monitoring task."""
    task_id: str
    warehouses: list[int] = Field(description="List of warehouse IDs to monitor")
    start_date: date
    end_date: date
    max_coefficient: float = Field(ge=0, le=50, description="Maximum acceptable coefficient")
    shipment_type: Literal["box", "monopallet"] = "box"
    mode: Literal["notify", "auto_book"] = "notify"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

    @validator('end_date')
    def end_date_must_be_after_start(cls, v, values):
        """Ensure end date is after start date."""
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class BookingRequest(BaseModel):
    """Request to book a slot."""
    warehouse_id: int
    date: str
    time: str
    shipment_type: str


class APIConfig(BaseModel):
    """API configuration."""
    wb_token: str = Field(min_length=10, description="Wildberries API token")
    telegram_bot_token: Optional[str] = Field(default=None, description="Telegram bot token")
    telegram_chat_id: Optional[str] = Field(default=None, description="Telegram chat ID")

    @validator('telegram_bot_token', 'telegram_chat_id')
    def validate_telegram_config(cls, v, values, field):
        """Ensure both telegram fields are provided together."""
        # If one is provided, both should be provided
        if field.name == 'telegram_chat_id':
            token = values.get('telegram_bot_token')
            if (token and not v) or (v and not token):
                raise ValueError('Both telegram_bot_token and telegram_chat_id must be provided together')
        return v


class LogEntry(BaseModel):
    """Log entry for the monitoring dashboard."""
    timestamp: datetime = Field(default_factory=datetime.now)
    level: Literal["INFO", "SUCCESS", "WARNING", "ERROR"] = "INFO"
    message: str
    task_id: Optional[str] = None

    def __str__(self) -> str:
        timestamp_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp_str}] {self.level}: {self.message}"
