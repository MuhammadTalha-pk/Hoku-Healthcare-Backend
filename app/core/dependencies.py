from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/token")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token, expected_type="access")
        user_id = int(payload["sub"])
        token_version = int(payload.get("ver", -1))
    except (ValueError, TypeError):
        raise credentials_exception

    user = db.get(User, user_id)
    if user is None or token_version != user.refresh_token_version:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user


def get_current_patient(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role != "patient":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Patient access required")
    return current_user


def get_current_doctor(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role not in {"doctor", "admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor access required")
    return current_user


def get_current_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required")
    return current_user


def verify_internal_api_key(
    x_internal_api_key: Annotated[str | None, Header(alias="X-Internal-API-Key")] = None,
) -> None:
    if not x_internal_api_key or not hmac_compare(x_internal_api_key, settings.INTERNAL_API_KEY):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal API key")


def hmac_compare(left: str, right: str) -> bool:
    import hmac

    return hmac.compare_digest(left.encode("utf-8"), right.encode("utf-8"))
