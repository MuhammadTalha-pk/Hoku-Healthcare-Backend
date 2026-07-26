"""Patient reviews API.

Original contributor: Faisal Majeed.
Integrated with Talha's authenticated user and PostgreSQL models.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin, get_current_patient, get_current_user
from app.models.doctor import Doctor
from app.models.review import Review
from app.models.user import User
from app.schemas.common_schema import MessageResponse
from app.schemas.review_schema import ReviewApproval, ReviewCreate, ReviewResponse, ReviewUpdate

router = APIRouter()


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    patient: User = Depends(get_current_patient),
) -> Review:
    if payload.doctor_id is not None and db.get(Doctor, payload.doctor_id) is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    review = Review(patient_id=patient.id, **payload.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.get("/", response_model=list[ReviewResponse])
def list_approved_reviews(db: Session = Depends(get_db)) -> list[Review]:
    query = select(Review).where(Review.is_approved.is_(True)).order_by(Review.created_at.desc())
    return list(db.scalars(query).all())


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(review_id: int, db: Session = Depends(get_db)) -> Review:
    review = db.get(Review, review_id)
    if review is None or not review.is_approved:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    payload: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Review:
    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    if current_user.role != "admin" and review.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="You may update only your own review")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(review, key, value)
    review.is_approved = False
    db.commit()
    db.refresh(review)
    return review


@router.patch("/{review_id}/approval", response_model=ReviewResponse)
def approve_or_reject_review(
    review_id: int,
    payload: ReviewApproval,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> Review:
    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    review.is_approved = payload.is_approved
    db.commit()
    db.refresh(review)
    return review


@router.delete("/{review_id}", response_model=MessageResponse)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    if current_user.role != "admin" and review.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="You may delete only your own review")
    db.delete(review)
    db.commit()
    return MessageResponse(message="Review deleted successfully")
