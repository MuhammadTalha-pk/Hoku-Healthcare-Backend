"""Review schemas based on Faisal Majeed's review module."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    doctor_id: int | None = Field(default=None, gt=0)
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=3, max_length=3000)


class ReviewUpdate(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    comment: str | None = Field(default=None, min_length=3, max_length=3000)


class ReviewApproval(BaseModel):
    is_approved: bool


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    doctor_id: int | None
    rating: int
    comment: str | None
    sentiment: str | None
    is_approved: bool
    created_at: datetime
