from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, ForeignKey, Index, String, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        Index("ix_appointment_doctor_slot", "doctor_id", "appointment_date", "appointment_time"),
        Index("ix_appointment_patient_date", "patient_id", "appointment_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id", ondelete="CASCADE"), index=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="RESTRICT"), index=True)
    appointment_date: Mapped[date] = mapped_column(Date, nullable=False)
    appointment_time: Mapped[time] = mapped_column(Time, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    patient = relationship("User", back_populates="appointments", foreign_keys=[patient_id])
    doctor = relationship("Doctor", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")
