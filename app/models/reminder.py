from datetime import date, datetime, time

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    medicine_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dosage: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reminder_time: Mapped[time] = mapped_column(Time, nullable=False)
    second_reminder_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    frequency: Mapped[str] = mapped_column(String(50), default="daily", nullable=False, index=True)
    weekly_days: Mapped[list[int] | None] = mapped_column(JSON, nullable=True)
    monthly_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Karachi", nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    last_sent: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_delivery_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    patient = relationship("User", back_populates="reminders")
