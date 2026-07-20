from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ReviewBase(BaseModel):
    patient_name: str = Field(
        min_length=2,
        max_length=255
    )

    rating: int = Field(
        ge=1,
        le=5
    )

    comment: str = Field(
        min_length=3
    )


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    patient_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=255
    )

    rating: Optional[int] = Field(
        default=None,
        ge=1,
        le=5
    )

    comment: Optional[str] = Field(
        default=None,
        min_length=3
    )


class ReviewApproval(BaseModel):
    is_approved: bool


class ReviewResponse(ReviewBase):
    id: int
    is_approved: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )