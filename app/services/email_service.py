import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DeliveryResult:
    success: bool
    provider: str
    message_id: str | None = None
    error: str | None = None


def send_email(to_email: str, subject: str, body: str) -> DeliveryResult:
    if settings.NOTIFICATION_MODE == "log":
        logger.info("[EMAIL-LOG] to=%s subject=%s body_length=%d", to_email, subject, len(body))
        return DeliveryResult(True, "log", message_id="logged-email")

    if not settings.SMTP_HOST or not settings.EMAIL_FROM:
        return DeliveryResult(False, "smtp", error="SMTP_HOST and EMAIL_FROM are required")

    message = EmailMessage()
    message["From"] = settings.EMAIL_FROM
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(message)
        return DeliveryResult(True, "smtp", message_id=message.get("Message-ID"))
    except Exception as exc:  # provider failures must not crash the scheduler
        logger.exception("Email delivery failed")
        return DeliveryResult(False, "smtp", error=str(exc))
