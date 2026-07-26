"""Healthcare services API.

Original contributor: Faisal Majeed.
Integrated with Talha's JWT/PostgreSQL backend architecture.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.service import Service
from app.models.user import User
from app.schemas.common_schema import MessageResponse
from app.schemas.service_schema import ServiceCreate, ServiceResponse, ServiceUpdate

router = APIRouter()


@router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(
    payload: ServiceCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> Service:
    if db.scalar(select(Service).where(Service.name == payload.name)):
        raise HTTPException(status_code=409, detail="A service with this name already exists")
    service = Service(**payload.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.get("/", response_model=list[ServiceResponse])
def list_services(db: Session = Depends(get_db)) -> list[Service]:
    return list(db.scalars(select(Service).where(Service.is_active.is_(True)).order_by(Service.name)).all())


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(service_id: int, db: Session = Depends(get_db)) -> Service:
    service = db.get(Service, service_id)
    if service is None or not service.is_active:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    payload: ServiceUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> Service:
    service = db.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    changes = payload.model_dump(exclude_unset=True)
    if "name" in changes:
        duplicate = db.scalar(select(Service).where(Service.name == changes["name"], Service.id != service_id))
        if duplicate:
            raise HTTPException(status_code=409, detail="A service with this name already exists")
    for key, value in changes.items():
        setattr(service, key, value)
    db.commit()
    db.refresh(service)
    return service


@router.delete("/{service_id}", response_model=MessageResponse)
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> MessageResponse:
    service = db.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    # Soft delete avoids breaking historical appointments.
    service.is_active = False
    db.commit()
    return MessageResponse(message="Service deactivated successfully")
