import base64
import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DeliveryResult:
    success: bool
    provider: str
    message_id: str | None = None
    error: str | None = None


def send_sms(to_phone: str, message: str) -> DeliveryResult:
    if settings.NOTIFICATION_MODE == "log":
        logger.info("[SMS-LOG] to=%s body=%s", to_phone, message)
        return DeliveryResult(True, "log", message_id="logged-sms")

    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
        return DeliveryResult(False, "twilio", error="Twilio configuration is incomplete")

    account_sid = settings.TWILIO_ACCOUNT_SID
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    payload = urllib.parse.urlencode(
        {"To": to_phone, "From": settings.TWILIO_PHONE_NUMBER, "Body": message}
    ).encode("utf-8")
    credentials = base64.b64encode(
        f"{account_sid}:{settings.TWILIO_AUTH_TOKEN}".encode("utf-8")
    ).decode("ascii")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Authorization": f"Basic {credentials}", "Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            response_body = response.read().decode("utf-8")
        parsed = json.loads(response_body)
        return DeliveryResult(True, "twilio", message_id=parsed.get("sid"))
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        logger.exception("SMS delivery failed")
        return DeliveryResult(False, "twilio", error=str(exc))
