from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


ReminderFrequency = Literal["daily", "twice_daily", "weekly", "monthly"]


class ReminderBase(BaseModel):
    medicine_name: str = Field(min_length=1, max_length=255)
    dosage: str | None = Field(default=None, max_length=100)
    reminder_time: time
    second_reminder_time: time | None = None
    frequency: ReminderFrequency = "daily"
    weekly_days: list[int] | None = None
    monthly_day: int | None = Field(default=None, ge=1, le=31)
    timezone: str = "Asia/Karachi"
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_schedule(self):
        if self.frequency == "twice_daily":
            if self.second_reminder_time is None:
                raise ValueError("second_reminder_time is required for twice_daily reminders")
            if self.second_reminder_time == self.reminder_time:
                raise ValueError("The two reminder times must be different")
        if self.frequency == "weekly":
            if not self.weekly_days:
                raise ValueError("weekly_days is required for weekly reminders")
            if any(day < 0 or day > 6 for day in self.weekly_days):
                raise ValueError("weekly_days values must be between 0 (Monday) and 6 (Sunday)")
            self.weekly_days = sorted(set(self.weekly_days))
        if self.frequency == "monthly" and self.monthly_day is None:
            raise ValueError("monthly_day is required for monthly reminders")
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date cannot be earlier than start_date")
        return self


class ReminderCreate(ReminderBase):
    pass


class ReminderUpdate(BaseModel):
    medicine_name: str | None = Field(default=None, min_length=1, max_length=255)
    dosage: str | None = Field(default=None, max_length=100)
    reminder_time: time | None = None
    second_reminder_time: time | None = None
    frequency: ReminderFrequency | None = None
    weekly_days: list[int] | None = None
    monthly_day: int | None = Field(default=None, ge=1, le=31)
    timezone: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None


class ReminderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    medicine_name: str
    dosage: str | None
    reminder_time: time
    second_reminder_time: time | None
    frequency: str
    weekly_days: list[int] | None
    monthly_day: int | None
    timezone: str
    start_date: date
    end_date: date | None
    is_active: bool
    next_run_at: datetime | None
    last_sent: datetime | None
    last_delivery_status: str | None
    created_at: datetime


class ReminderSendRequest(BaseModel):
    reminder_id: int = Field(gt=0)
