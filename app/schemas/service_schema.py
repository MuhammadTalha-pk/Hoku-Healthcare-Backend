"""Healthcare service schemas based on Faisal Majeed's services module."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ServiceBase(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = None
    price: Decimal | None = Field(default=None, ge=0)
    image_url: str | None = Field(default=None, max_length=500)
    is_active: bool = True


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    price: Decimal | None = Field(default=None, ge=0)
    image_url: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class ServiceResponse(ServiceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
