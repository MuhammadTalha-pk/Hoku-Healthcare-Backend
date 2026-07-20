from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import Optional


class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Optional[Decimal] = None
    image_url: Optional[str] = None
    is_active: bool = True


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class ServiceResponse(ServiceBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)