from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_doctor, get_current_patient, get_current_user
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.doctor_availability import DoctorAvailability
from app.models.service import Service
from app.models.user import User
from app.schemas.appointment_schema import (
    AppointmentCancel,
    AppointmentCreate,
    AppointmentResponse,
    AppointmentStatusUpdate,
)

router = APIRouter()
ACTIVE_STATUSES = {"pending", "confirmed"}
ALLOWED_TRANSITIONS = {
    "pending": {"confirmed", "rejected", "cancelled"},
    "confirmed": {"completed", "cancelled", "no_show"},
    "completed": set(),
    "cancelled": set(),
    "rejected": set(),
    "no_show": set(),
}


def _doctor_profile(db: Session, user: User) -> Doctor:
    doctor = db.scalar(select(Doctor).where(Doctor.user_id == user.id))
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    return doctor


def _appointment_datetime(payload: AppointmentCreate | Appointment) -> datetime:
    local = datetime.combine(
        payload.appointment_date, payload.appointment_time, tzinfo=ZoneInfo(settings.DEFAULT_TIMEZONE)
    )
    return local.astimezone(UTC)


def _validate_booking(db: Session, payload: AppointmentCreate) -> tuple[Doctor, Service]:
    appointment_dt = _appointment_datetime(payload)
    if appointment_dt <= datetime.now(UTC):
        raise HTTPException(status_code=400, detail="Appointment must be scheduled in the future")

    doctor = db.get(Doctor, payload.doctor_id)
    if doctor is None or not doctor.is_available or not doctor.user.is_active:
        raise HTTPException(status_code=404, detail="Available doctor not found")
    service = db.get(Service, payload.service_id)
    if service is None or not service.is_active:
        raise HTTPException(status_code=404, detail="Active service not found")

    weekday = payload.appointment_date.strftime("%A")
    slot = db.scalar(
        select(DoctorAvailability).where(
            DoctorAvailability.doctor_id == doctor.id,
            DoctorAvailability.day_of_week == weekday,
            DoctorAvailability.is_available.is_(True),
            DoctorAvailability.start_time <= payload.appointment_time,
            DoctorAvailability.end_time > payload.appointment_time,
        )
    )
    if slot is None:
        raise HTTPException(status_code=400, detail="Doctor is not available at the selected time")

    duplicate = db.scalar(
        select(Appointment).where(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date == payload.appointment_date,
            Appointment.appointment_time == payload.appointment_time,
            Appointment.status.in_(ACTIVE_STATUSES),
        )
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="The selected doctor time slot is already booked")
    return doctor, service


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def book_appointment(
    payload: AppointmentCreate,
    patient: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
) -> Appointment:
    _validate_booking(db, payload)
    patient_conflict = db.scalar(
        select(Appointment).where(
            Appointment.patient_id == patient.id,
            Appointment.appointment_date == payload.appointment_date,
            Appointment.appointment_time == payload.appointment_time,
            Appointment.status.in_(ACTIVE_STATUSES),
        )
    )
    if patient_conflict:
        raise HTTPException(status_code=409, detail="You already have an appointment at this time")
    appointment = Appointment(patient_id=patient.id, **payload.model_dump())
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("/patient", response_model=list[AppointmentResponse])
def patient_appointments(
    patient: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
) -> list[Appointment]:
    return list(
        db.scalars(
            select(Appointment)
            .where(Appointment.patient_id == patient.id)
            .order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc())
        ).all()
    )


@router.get("/doctor", response_model=list[AppointmentResponse])
def doctor_appointments(
    status_filter: str | None = Query(default=None, alias="status"),
    doctor_user: User = Depends(get_current_doctor),
    db: Session = Depends(get_db),
) -> list[Appointment]:
    doctor = _doctor_profile(db, doctor_user)
    statement = select(Appointment).where(Appointment.doctor_id == doctor.id)
    if status_filter:
        statement = statement.where(Appointment.status == status_filter)
    return list(db.scalars(statement.order_by(Appointment.appointment_date, Appointment.appointment_time)).all())


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def appointment_details(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Appointment:
    appointment = db.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    allowed = current_user.role == "admin" or appointment.patient_id == current_user.id
    if current_user.role == "doctor":
        doctor = _doctor_profile(db, current_user)
        allowed = appointment.doctor_id == doctor.id
    if not allowed:
        raise HTTPException(status_code=403, detail="You cannot access this appointment")
    return appointment


@router.put("/{appointment_id}/status", response_model=AppointmentResponse)
def update_status(
    appointment_id: int,
    payload: AppointmentStatusUpdate,
    doctor_user: User = Depends(get_current_doctor),
    db: Session = Depends(get_db),
) -> Appointment:
    appointment = db.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if doctor_user.role != "admin":
        doctor = _doctor_profile(db, doctor_user)
        if appointment.doctor_id != doctor.id:
            raise HTTPException(status_code=403, detail="You can update only your own appointments")
    if payload.status not in ALLOWED_TRANSITIONS.get(appointment.status, set()):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot change status from {appointment.status} to {payload.status}",
        )
    appointment.status = payload.status
    db.commit()
    db.refresh(appointment)
    return appointment


@router.put("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(
    appointment_id: int,
    payload: AppointmentCancel,
    patient: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
) -> Appointment:
    appointment = db.get(Appointment, appointment_id)
    if appointment is None or appointment.patient_id != patient.id:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appointment.status not in ACTIVE_STATUSES:
        raise HTTPException(status_code=400, detail="This appointment cannot be cancelled")
    if _appointment_datetime(appointment) - datetime.now(UTC) < timedelta(hours=24):
        raise HTTPException(status_code=400, detail="Appointments must be cancelled at least 24 hours in advance")
    appointment.status = "cancelled"
    appointment.cancellation_reason = payload.reason
    db.commit()
    db.refresh(appointment)
    return appointment
