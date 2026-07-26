from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    specialty: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    experience_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    qualification: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    consultation_fee: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="doctor_profile")
    availability = relationship(
        "DoctorAvailability", back_populates="doctor", cascade="all, delete-orphan", order_by="DoctorAvailability.day_of_week"
    )
    appointments = relationship("Appointment", back_populates="doctor")
