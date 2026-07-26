from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=1000)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class PatientRegister(UserBase):
    password: str = Field(min_length=8, max_length=128)


class DoctorRegister(UserBase):
    password: str = Field(min_length=8, max_length=128)
    specialty: str = Field(min_length=2, max_length=255)
    experience_years: int | None = Field(default=None, ge=0, le=80)
    qualification: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=3000)
    consultation_fee: float | None = Field(default=None, ge=0)


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=1000)


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
