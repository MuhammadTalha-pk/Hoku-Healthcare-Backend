import calendar
import logging
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.notification import Notification
from app.models.reminder import Reminder
from app.models.user import User
from app.services.email_service import send_email
from app.services.sms_service import send_sms

logger = logging.getLogger(__name__)


def ensure_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


@dataclass(slots=True)
class ReminderDelivery:
    reminder_id: int
    email_sent: bool
    sms_sent: bool
    status: str
    next_run_at: datetime | None


def validate_timezone(timezone_name: str) -> ZoneInfo:
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Unknown timezone: {timezone_name}") from exc


def _local_datetime(day: date, at_time: time, timezone_name: str) -> datetime:
    tz = validate_timezone(timezone_name)
    return datetime.combine(day, at_time, tzinfo=tz)


def _candidate_times(reminder: Reminder) -> list[time]:
    times = [reminder.reminder_time]
    if reminder.frequency == "twice_daily" and reminder.second_reminder_time:
        times.append(reminder.second_reminder_time)
    return sorted(times)


def calculate_next_run(reminder: Reminder, after_utc: datetime | None = None) -> datetime | None:
    if reminder.is_active is False:
        return None

    now_utc = after_utc or datetime.now(UTC)
    now_utc = ensure_utc(now_utc)
    tz = validate_timezone(reminder.timezone)
    local_now = now_utc.astimezone(tz)
    start_date = reminder.start_date
    end_date = reminder.end_date

    def valid_date(candidate: date) -> bool:
        return candidate >= start_date and (end_date is None or candidate <= end_date)

    frequency = reminder.frequency
    times = _candidate_times(reminder)

    # Search a bounded future horizon. Monthly reminders need up to several years for day 31.
    for offset in range(0, 366 * 5):
        candidate_date = local_now.date() + timedelta(days=offset)
        if not valid_date(candidate_date):
            if end_date and candidate_date > end_date:
                return None
            continue

        if frequency == "weekly" and candidate_date.weekday() not in (reminder.weekly_days or []):
            continue
        if frequency == "monthly":
            required_day = reminder.monthly_day or 1
            last_day = calendar.monthrange(candidate_date.year, candidate_date.month)[1]
            if required_day > last_day or candidate_date.day != required_day:
                continue

        for candidate_time in times:
            candidate_local = _local_datetime(candidate_date, candidate_time, reminder.timezone)
            if candidate_local > local_now:
                return candidate_local.astimezone(UTC)
    return None


def prepare_new_reminder(reminder: Reminder) -> None:
    validate_timezone(reminder.timezone)
    now = datetime.now(UTC) - timedelta(seconds=1)
    reminder.next_run_at = calculate_next_run(reminder, after_utc=now)


def _message_for(reminder: Reminder, user: User) -> tuple[str, str]:
    subject = "Hoku Health Care - Medication Reminder"
    display_time = reminder.next_run_at
    if display_time:
        display_time = ensure_utc(display_time).astimezone(validate_timezone(reminder.timezone))
        time_text = display_time.strftime("%I:%M %p")
    else:
        time_text = reminder.reminder_time.strftime("%I:%M %p")
    body = (
        f"Dear {user.full_name},\n\n"
        f"This is your medication reminder.\n"
        f"Medicine: {reminder.medicine_name}\n"
        f"Dosage: {reminder.dosage or 'As prescribed'}\n"
        f"Scheduled time: {time_text}\n\n"
        "Please follow the instructions given by your healthcare professional.\n\n"
        "Best regards,\nHoku Health Care Team"
    )
    return subject, body


def deliver_reminder(db: Session, reminder: Reminder, force: bool = False) -> ReminderDelivery:
    now = datetime.now(UTC)
    if not force:
        stored_next_run = ensure_utc(reminder.next_run_at) if reminder.next_run_at else None
        if not reminder.is_active or stored_next_run is None or stored_next_run > now:
            return ReminderDelivery(reminder.id, False, False, "not_due", stored_next_run)

    user = db.get(User, reminder.patient_id)
    if user is None or not user.is_active:
        reminder.last_delivery_status = "patient_unavailable"
        reminder.next_run_at = None
        db.commit()
        return ReminderDelivery(reminder.id, False, False, "patient_unavailable", None)

    subject, body = _message_for(reminder, user)
    email_result = send_email(user.email, subject, body)
    sms_result = send_sms(user.phone, body) if user.phone else None
    email_sent = email_result.success
    sms_sent = bool(sms_result and sms_result.success)

    if email_sent or sms_sent:
        status = "sent" if email_sent and (sms_sent or not user.phone) else "partially_sent"
        reminder.last_sent = now
        reminder.last_delivery_status = status
        reminder.next_run_at = calculate_next_run(reminder, after_utc=now + timedelta(seconds=1))
    else:
        status = "failed"
        reminder.last_delivery_status = status
        reminder.next_run_at = now + timedelta(minutes=settings.REMINDER_RETRY_MINUTES)

    db.add(
        Notification(
            user_id=user.id,
            title=subject,
            message=body,
            type="reminder",
            channel="email+sms" if user.phone else "email",
            delivery_status=status,
        )
    )
    db.commit()
    db.refresh(reminder)
    return ReminderDelivery(reminder.id, email_sent, sms_sent, status, reminder.next_run_at)


def process_due_reminders(db: Session, limit: int = 100) -> list[ReminderDelivery]:
    now = datetime.now(UTC)
    statement = (
        select(Reminder)
        .where(Reminder.is_active.is_(True), Reminder.next_run_at.is_not(None), Reminder.next_run_at <= now)
        .order_by(Reminder.next_run_at)
        .limit(limit)
    )
    if db.bind is not None and db.bind.dialect.name == "postgresql":
        statement = statement.with_for_update(skip_locked=True)

    reminders = list(db.scalars(statement).all())
    results: list[ReminderDelivery] = []
    for reminder in reminders:
        try:
            results.append(deliver_reminder(db, reminder))
        except Exception:
            logger.exception("Failed to process reminder %s", reminder.id)
            db.rollback()
    return results
