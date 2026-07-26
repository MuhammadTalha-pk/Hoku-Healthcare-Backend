import base64
import hashlib
import hmac
import os
from datetime import UTC, datetime, timedelta
from typing import Any, Literal
from uuid import uuid4

import jwt
from jwt import InvalidTokenError

from app.core.config import settings

try:
    import bcrypt  # type: ignore
except ImportError:  # pragma: no cover - secure fallback is covered instead
    bcrypt = None


TokenType = Literal["access", "refresh", "password_reset"]


def get_password_hash(password: str) -> str:
    if bcrypt is not None:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

    # Secure fallback for environments where bcrypt has not yet been installed.
    salt = os.urandom(16)
    iterations = 600_000
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return "pbkdf2_sha256${}${}${}".format(
        iterations,
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(digest).decode("ascii"),
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if hashed_password.startswith("$2") and bcrypt is not None:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

    try:
        algorithm, iterations_text, salt_text, digest_text = hashed_password.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_text)
        salt = base64.urlsafe_b64decode(salt_text.encode("ascii"))
        expected = base64.urlsafe_b64decode(digest_text.encode("ascii"))
        calculated = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(calculated, expected)
    except (ValueError, TypeError):
        return False


def _create_token(
    subject: int | str,
    token_type: TokenType,
    expires_delta: timedelta,
    token_version: int = 0,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": token_type,
        "ver": token_version,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid4()),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: int | str, token_version: int = 0) -> str:
    return _create_token(
        subject,
        "access",
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_version,
    )


def create_refresh_token(subject: int | str, token_version: int = 0) -> str:
    return _create_token(
        subject,
        "refresh",
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_version,
    )


def create_password_reset_token(subject: int | str, token_version: int = 0) -> str:
    return _create_token(
        subject,
        "password_reset",
        timedelta(minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES),
        token_version,
    )


def decode_token(token: str, expected_type: TokenType | None = None) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except InvalidTokenError as exc:
        raise ValueError("Invalid or expired token") from exc

    if expected_type and payload.get("type") != expected_type:
        raise ValueError(f"Expected a {expected_type} token")
    if payload.get("sub") is None:
        raise ValueError("Token subject is missing")
    return payload
