from fastapi import APIRouter

from app.schemas.doctor_recommender import (
    DoctorRecommendationRequest,
    DoctorRecommendationResponse,
)
from app.services.doctor_recommender_service import (
    get_specialties,
    recommend_doctor,
)


router = APIRouter(
    prefix="/api/doctor-recommender",
    tags=["AI Doctor Recommender"],
)


@router.post(
    "/recommend",
    response_model=DoctorRecommendationResponse,
)
def recommend_doctor_endpoint(
    request: DoctorRecommendationRequest,
):
    return recommend_doctor(request)


@router.get("/specialties")
def get_available_specialties():
    return {
        "total": len(get_specialties()),
        "specialties": get_specialties(),
    }