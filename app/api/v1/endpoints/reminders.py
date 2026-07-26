from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_patient
from app.models.reminder import Reminder
from app.models.user import User
from app.schemas.common_schema import MessageResponse
from app.schemas.reminder_schema import ReminderCreate, ReminderResponse, ReminderUpdate
from app.services.reminder_service import prepare_new_reminder, validate_timezone

router = APIRouter()


def _owned_reminder(db: Session, reminder_id: int, patient_id: int) -> Reminder:
    reminder = db.scalar(
        select(Reminder).where(Reminder.id == reminder_id, Reminder.patient_id == patient_id)
    )
    if reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder


def _validate_fields(data: dict) -> None:
    timezone_name = data.get("timezone") or settings.DEFAULT_TIMEZONE
    validate_timezone(timezone_name)
    frequency = data.get("frequency", "daily")
    if frequency == "twice_daily" and not data.get("second_reminder_time"):
        raise HTTPException(status_code=422, detail="second_reminder_time is required for twice_daily reminders")
    if frequency == "weekly" and not data.get("weekly_days"):
        raise HTTPException(status_code=422, detail="weekly_days is required for weekly reminders")
    if frequency == "monthly" and not data.get("monthly_day"):
        raise HTTPException(status_code=422, detail="monthly_day is required for monthly reminders")


@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
def create_reminder(
    payload: ReminderCreate,
    patient: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
) -> Reminder:
    data = payload.model_dump()
    data["start_date"] = data["start_date"] or datetime.now(validate_timezone(data["timezone"])).date()
    _validate_fields(data)
    reminder = Reminder(patient_id=patient.id, **data)
    prepare_new_reminder(reminder)
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.get("/", response_model=list[ReminderResponse])
def list_reminders(
    patient: User = Depends(get_current_patient), db: Session = Depends(get_db)
) -> list[Reminder]:
    return list(
        db.scalars(
            select(Reminder).where(Reminder.patient_id == patient.id).order_by(Reminder.created_at.desc())
        ).all()
    )


@router.get("/{reminder_id}", response_model=ReminderResponse)
def get_reminder(
    reminder_id: int,
    patient: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
) -> Reminder:
    return _owned_reminder(db, reminder_id, patient.id)


@router.put("/{reminder_id}", response_model=ReminderResponse)
def update_reminder(
    reminder_id: int,
    payload: ReminderUpdate,
    patient: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
) -> Reminder:
    reminder = _owned_reminder(db, reminder_id, patient.id)
    changes = payload.model_dump(exclude_unset=True)
    current = {
        "medicine_name": reminder.medicine_name,
        "dosage": reminder.dosage,
        "reminder_time": reminder.reminder_time,
        "second_reminder_time": reminder.second_reminder_time,
        "frequency": reminder.frequency,
        "weekly_days": reminder.weekly_days,
        "monthly_day": reminder.monthly_day,
        "timezone": reminder.timezone,
        "start_date": reminder.start_date,
        "end_date": reminder.end_date,
    }
    current.update({key: value for key, value in changes.items() if key != "is_active"})
    validated = ReminderCreate.model_validate(current)
    _validate_fields(validated.model_dump())
    for field, value in validated.model_dump().items():
        setattr(reminder, field, value)
    if "is_active" in changes:
        reminder.is_active = changes["is_active"]
    prepare_new_reminder(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.delete("/{reminder_id}", response_model=MessageResponse)
def delete_reminder(
    reminder_id: int,
    patient: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
) -> MessageResponse:
    reminder = _owned_reminder(db, reminder_id, patient.id)
    db.delete(reminder)
    db.commit()
    return MessageResponse(message="Reminder deleted successfully")
