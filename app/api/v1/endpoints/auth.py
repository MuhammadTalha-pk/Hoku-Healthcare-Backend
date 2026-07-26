from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.common_schema import MessageResponse
from app.schemas.user_schema import (
    DoctorRegister,
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    PatientRegister,
    RefreshRequest,
    TokenResponse,
    UserResponse,
)
from app.services.email_service import send_email

router = APIRouter()


def _find_user(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.strip().lower()))


def _tokens(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user.id, user.refresh_token_version),
        refresh_token=create_refresh_token(user.id, user.refresh_token_version),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user,
    )


def _authenticate(db: Session, email: str, password: str) -> User:
    user = _find_user(db, email)
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive account")
    return user


@router.post("/register/patient", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_patient(payload: PatientRegister, db: Session = Depends(get_db)) -> User:
    if _find_user(db, str(payload.email)):
        raise HTTPException(status_code=409, detail="Email is already registered")
    user = User(
        full_name=payload.full_name,
        email=str(payload.email).lower(),
        phone=payload.phone,
        address=payload.address,
        role="patient",
        password_hash=get_password_hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/register/doctor", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_doctor(payload: DoctorRegister, db: Session = Depends(get_db)) -> User:
    if _find_user(db, str(payload.email)):
        raise HTTPException(status_code=409, detail="Email is already registered")
    user = User(
        full_name=payload.full_name,
        email=str(payload.email).lower(),
        phone=payload.phone,
        address=payload.address,
        role="doctor",
        password_hash=get_password_hash(payload.password),
    )
    user.doctor_profile = Doctor(
        specialty=payload.specialty,
        experience_years=payload.experience_years,
        qualification=payload.qualification,
        bio=payload.bio,
        consultation_fee=payload.consultation_fee,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return _tokens(_authenticate(db, str(payload.email), payload.password))


@router.post("/token", response_model=TokenResponse)
def oauth2_token(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> TokenResponse:
    return _tokens(_authenticate(db, form.username, form.password))


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        token_payload = decode_token(payload.refresh_token, expected_type="refresh")
        user_id = int(token_payload["sub"])
        token_version = int(token_payload.get("ver", -1))
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = db.get(User, user_id)
    if user is None or not user.is_active or token_version != user.refresh_token_version:
        raise HTTPException(status_code=401, detail="Refresh token is no longer valid")
    return _tokens(user)


@router.post("/logout", response_model=MessageResponse)
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MessageResponse:
    current_user.refresh_token_version += 1
    db.commit()
    return MessageResponse(message="Logged out successfully. Existing tokens have been revoked.")


@router.post("/password-reset/request", response_model=MessageResponse)
def request_password_reset(payload: PasswordResetRequest, db: Session = Depends(get_db)) -> MessageResponse:
    user = _find_user(db, str(payload.email))
    if user and user.is_active:
        token = create_password_reset_token(user.id, user.refresh_token_version)
        send_email(
            user.email,
            "Hoku Health Care - Password Reset",
            "Use this password reset token within "
            f"{settings.PASSWORD_RESET_EXPIRE_MINUTES} minutes:\n\n{token}",
        )
    return MessageResponse(message="If the email is registered, password reset instructions have been sent.")


@router.post("/password-reset/confirm", response_model=MessageResponse)
def confirm_password_reset(payload: PasswordResetConfirm, db: Session = Depends(get_db)) -> MessageResponse:
    try:
        token_payload = decode_token(payload.token, expected_type="password_reset")
        user_id = int(token_payload["sub"])
        token_version = int(token_payload.get("ver", -1))
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid or expired password reset token")
    user = db.get(User, user_id)
    if user is None or token_version != user.refresh_token_version:
        raise HTTPException(status_code=400, detail="Password reset token is no longer valid")
    user.password_hash = get_password_hash(payload.new_password)
    user.refresh_token_version += 1
    db.commit()
    return MessageResponse(message="Password reset successfully")
