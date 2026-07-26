"""AI health tips endpoint. Original contributor: Faisal Majeed."""

from fastapi import APIRouter, HTTPException, status

from app.schemas.health_tips import HealthTipsRequest, HealthTipsResponse
from app.services.health_tips_service import HealthTipsConfigurationError, HealthTipsServiceError, generate_health_tips

router = APIRouter()
CATEGORIES = [
    "general wellness", "heart health", "diabetes care", "weight management",
    "healthy diet", "sleep improvement", "stress management", "hydration",
    "exercise", "mental wellness",
]


@router.post("/health-tips", response_model=HealthTipsResponse)
def generate_health_tips_endpoint(payload: HealthTipsRequest) -> HealthTipsResponse:
    try:
        return generate_health_tips(payload)
    except HealthTipsConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except HealthTipsServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get("/health-tip-categories")
def health_tip_categories() -> dict[str, object]:
    return {"total": len(CATEGORIES), "categories": CATEGORIES}
