from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.user_schema import UserResponse


VALID_DAYS = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}


class AvailabilitySlot(BaseModel):
    day_of_week: str
    start_time: time
    end_time: time
    is_available: bool = True

    @model_validator(mode="after")
    def validate_slot(self):
        normalized = self.day_of_week.strip().title()
        if normalized not in VALID_DAYS:
            raise ValueError("day_of_week must be a valid English weekday")
        self.day_of_week = normalized
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be earlier than end_time")
        return self


class AvailabilityReplace(BaseModel):
    slots: list[AvailabilitySlot] = Field(min_length=1, max_length=50)

    @model_validator(mode="after")
    def reject_overlaps(self):
        grouped: dict[str, list[tuple[time, time]]] = {}
        for slot in self.slots:
            grouped.setdefault(slot.day_of_week, []).append((slot.start_time, slot.end_time))
        for day, ranges in grouped.items():
            ranges.sort()
            for previous, current in zip(ranges, ranges[1:]):
                if current[0] < previous[1]:
                    raise ValueError(f"Overlapping availability slots found for {day}")
        return self


class AvailabilityResponse(AvailabilitySlot):
    model_config = ConfigDict(from_attributes=True)

    id: int
    doctor_id: int


class DoctorUpdate(BaseModel):
    specialty: str | None = Field(default=None, min_length=2, max_length=255)
    experience_years: int | None = Field(default=None, ge=0, le=80)
    qualification: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=3000)
    consultation_fee: float | None = Field(default=None, ge=0)
    is_available: bool | None = None


class DoctorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    specialty: str
    experience_years: int | None
    qualification: str | None
    bio: str | None
    consultation_fee: float | None
    is_available: bool
    created_at: datetime
    user: UserResponse
    availability: list[AvailabilityResponse] = Field(default_factory=list)
