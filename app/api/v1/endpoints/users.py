from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin, get_current_user
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.common_schema import MessageResponse
from app.schemas.user_schema import PasswordChange, UserResponse, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.put("/me", response_model=UserResponse)
def update_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    changes = payload.model_dump(exclude_unset=True)
    if "phone" in changes and changes["phone"]:
        duplicate = db.scalar(select(User).where(User.phone == changes["phone"], User.id != current_user.id))
        if duplicate:
            raise HTTPException(status_code=409, detail="Phone number is already in use")
    for field, value in changes.items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/me/password", response_model=MessageResponse)
def change_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.password_hash = get_password_hash(payload.new_password)
    current_user.refresh_token_version += 1
    db.commit()
    return MessageResponse(message="Password changed successfully; existing tokens were revoked")


@router.get("/patients", response_model=list[UserResponse])
def list_patients(
    active_only: bool = Query(default=False),
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[User]:
    statement = select(User).where(User.role == "patient").order_by(User.created_at.desc())
    if active_only:
        statement = statement.where(User.is_active.is_(True))
    return list(db.scalars(statement).all())


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, _: User = Depends(get_current_admin), db: Session = Depends(get_db)) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}/active", response_model=UserResponse)
def set_user_active(
    user_id: int,
    is_active: bool,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> User:
    if user_id == admin.id and not is_active:
        raise HTTPException(status_code=400, detail="You cannot deactivate your own administrator account")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = is_active
    if not is_active:
        user.refresh_token_version += 1
    db.commit()
    db.refresh(user)
    return user
