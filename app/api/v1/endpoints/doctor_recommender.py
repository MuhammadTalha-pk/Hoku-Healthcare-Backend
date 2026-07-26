"""AI doctor recommender endpoint. Original contributor: Faisal Majeed."""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.doctor_recommender import DoctorRecommendationRequest, DoctorRecommendationResponse
from app.services.doctor_recommender_service import get_specialties, recommend_doctor

router = APIRouter()


@router.post("/recommend-doctor", response_model=DoctorRecommendationResponse)
def recommend_doctor_endpoint(
    payload: DoctorRecommendationRequest,
    _: User = Depends(get_current_user),
) -> DoctorRecommendationResponse:
    return recommend_doctor(payload)


@router.get("/doctor-specialties")
def available_specialties() -> dict[str, object]:
    specialties = get_specialties()
    return {"total": len(specialties), "specialties": specialties}
