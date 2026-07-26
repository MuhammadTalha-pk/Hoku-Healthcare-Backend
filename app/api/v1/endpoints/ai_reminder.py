from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import verify_internal_api_key
from app.models.reminder import Reminder
from app.schemas.reminder_schema import ReminderSendRequest
from app.services.reminder_service import deliver_reminder

router = APIRouter()


@router.post("/reminder/send")
def send_medication_reminder(
    payload: ReminderSendRequest,
    _: None = Depends(verify_internal_api_key),
    db: Session = Depends(get_db),
) -> dict:
    reminder = db.get(Reminder, payload.reminder_id)
    if reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return asdict(deliver_reminder(db, reminder, force=True))
