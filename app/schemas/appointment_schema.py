from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


AppointmentStatus = Literal["pending", "confirmed", "completed", "cancelled", "rejected", "no_show"]


class AppointmentCreate(BaseModel):
    doctor_id: int = Field(gt=0)
    service_id: int = Field(gt=0)
    appointment_date: date
    appointment_time: time
    notes: str | None = Field(default=None, max_length=2000)


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


class AppointmentCancel(BaseModel):
    reason: str | None = Field(default=None, max_length=1000)


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    doctor_id: int
    service_id: int
    appointment_date: date
    appointment_time: time
    status: str
    notes: str | None
    cancellation_reason: str | None
    created_at: datetime
