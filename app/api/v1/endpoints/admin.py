"""Administrative API. Original contributor: Faisal Majeed."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.review import Review
from app.models.service import Service
from app.models.user import User
from app.schemas.admin import AdminDashboardResponse
from app.schemas.review_schema import ReviewResponse
from app.schemas.service_schema import ServiceResponse

router = APIRouter()


@router.get("/dashboard", response_model=AdminDashboardResponse)
def dashboard(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> AdminDashboardResponse:
    avg_rating = db.scalar(select(func.avg(Review.rating))) or 0
    return AdminDashboardResponse(
        total_users=db.scalar(select(func.count(User.id))) or 0,
        total_patients=db.scalar(select(func.count(User.id)).where(User.role == "patient")) or 0,
        total_doctors=db.scalar(select(func.count(Doctor.id))) or 0,
        total_appointments=db.scalar(select(func.count(Appointment.id))) or 0,
        total_services=db.scalar(select(func.count(Service.id))) or 0,
        active_services=db.scalar(select(func.count(Service.id)).where(Service.is_active.is_(True))) or 0,
        total_reviews=db.scalar(select(func.count(Review.id))) or 0,
        approved_reviews=db.scalar(select(func.count(Review.id)).where(Review.is_approved.is_(True))) or 0,
        pending_reviews=db.scalar(select(func.count(Review.id)).where(Review.is_approved.is_(False))) or 0,
        average_rating=round(float(avg_rating), 2),
    )


@router.get("/services", response_model=list[ServiceResponse])
def all_services(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> list[Service]:
    return list(db.scalars(select(Service).order_by(Service.created_at.desc())).all())


@router.get("/reviews", response_model=list[ReviewResponse])
def all_reviews(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> list[Review]:
    return list(db.scalars(select(Review).order_by(Review.created_at.desc())).all())


@router.get("/reviews/pending", response_model=list[ReviewResponse])
def pending_reviews(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> list[Review]:
    return list(db.scalars(select(Review).where(Review.is_approved.is_(False))).all())
