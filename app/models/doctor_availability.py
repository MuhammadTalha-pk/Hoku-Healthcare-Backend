from datetime import time

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DoctorAvailability(Base):
    __tablename__ = "doctor_availability"
    __table_args__ = (
        CheckConstraint("start_time < end_time", name="ck_availability_start_before_end"),
        UniqueConstraint("doctor_id", "day_of_week", "start_time", "end_time", name="uq_doctor_availability_slot"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id", ondelete="CASCADE"), index=True)
    day_of_week: Mapped[str] = mapped_column(String(20), index=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    doctor = relationship("Doctor", back_populates="availability")
