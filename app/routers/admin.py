from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.service import Service
from app.models.review import Review
from app.schemas.service import ServiceResponse
from app.schemas.review import ReviewResponse
from app.schemas.admin import AdminDashboardResponse


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/dashboard", response_model=AdminDashboardResponse)
def get_admin_dashboard(db: Session = Depends(get_db)):
    total_services = db.query(Service).count()

    active_services = (
        db.query(Service)
        .filter(Service.is_active.is_(True))
        .count()
    )

    total_reviews = db.query(Review).count()

    approved_reviews = (
        db.query(Review)
        .filter(Review.is_approved.is_(True))
        .count()
    )

    pending_reviews = (
        db.query(Review)
        .filter(Review.is_approved.is_(False))
        .count()
    )

    average_rating = db.query(func.avg(Review.rating)).scalar()

    return {
        "total_services": total_services,
        "active_services": active_services,
        "total_reviews": total_reviews,
        "approved_reviews": approved_reviews,
        "pending_reviews": pending_reviews,
        "average_rating": round(float(average_rating or 0), 2)
    }


@router.get("/services", response_model=list[ServiceResponse])
def get_all_services_for_admin(db: Session = Depends(get_db)):
    return db.query(Service).all()


@router.get("/reviews", response_model=list[ReviewResponse])
def get_all_reviews_for_admin(db: Session = Depends(get_db)):
    return db.query(Review).all()


@router.get("/reviews/pending", response_model=list[ReviewResponse])
def get_pending_reviews(db: Session = Depends(get_db)):
    return (
        db.query(Review)
        .filter(Review.is_approved.is_(False))
        .all()
    )


@router.patch(
    "/reviews/{review_id}/approve",
    response_model=ReviewResponse
)
def approve_review(
    review_id: int,
    db: Session = Depends(get_db)
):
    review = (
        db.query(Review)
        .filter(Review.id == review_id)
        .first()
    )

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    review.is_approved = True
    db.commit()
    db.refresh(review)

    return review


@router.delete("/services/{service_id}")
def delete_service_by_admin(
    service_id: int,
    db: Session = Depends(get_db)
):
    service = (
        db.query(Service)
        .filter(Service.id == service_id)
        .first()
    )

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    db.delete(service)
    db.commit()

    return {
        "message": "Service deleted successfully by admin"
    }


@router.delete("/reviews/{review_id}")
def delete_review_by_admin(
    review_id: int,
    db: Session = Depends(get_db)
):
    review = (
        db.query(Review)
        .filter(Review.id == review_id)
        .first()
    )

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    db.delete(review)
    db.commit()

    return {
        "message": "Review deleted successfully by admin"
    }