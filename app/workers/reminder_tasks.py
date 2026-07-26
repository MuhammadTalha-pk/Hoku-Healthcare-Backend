import logging
import threading
from datetime import UTC, datetime

from app.core.config import settings
from app.core.database import SessionLocal
from app.services.reminder_service import process_due_reminders

logger = logging.getLogger(__name__)
_stop_event = threading.Event()
_worker_thread: threading.Thread | None = None
_lock = threading.Lock()


def reminder_job() -> int:
    db = SessionLocal()
    try:
        results = process_due_reminders(db)
        logger.info("Reminder job completed at %s; processed=%s", datetime.now(UTC).isoformat(), len(results))
        return len(results)
    finally:
        db.close()


def _worker_loop() -> None:
    while not _stop_event.is_set():
        try:
            reminder_job()
        except Exception:
            logger.exception("Unhandled reminder worker error")
        _stop_event.wait(settings.REMINDER_CHECK_INTERVAL_SECONDS)


def start_reminder_scheduler() -> None:
    global _worker_thread
    if not settings.ENABLE_SCHEDULER:
        logger.info("Medication reminder scheduler is disabled")
        return
    with _lock:
        if _worker_thread and _worker_thread.is_alive():
            return
        _stop_event.clear()
        _worker_thread = threading.Thread(target=_worker_loop, name="hoku-reminder-worker", daemon=True)
        _worker_thread.start()
        logger.info("Medication reminder scheduler started")


def stop_reminder_scheduler() -> None:
    global _worker_thread
    with _lock:
        _stop_event.set()
        if _worker_thread and _worker_thread.is_alive():
            _worker_thread.join(timeout=5)
        _worker_thread = None
        logger.info("Medication reminder scheduler stopped")
