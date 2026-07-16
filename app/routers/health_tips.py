from fastapi import APIRouter, HTTPException, status

from app.schemas.health_tips import (
    HealthTipsRequest,
    HealthTipsResponse,
)
from app.services.health_tips_service import (
    HealthTipsConfigurationError,
    HealthTipsServiceError,
    generate_health_tips,
)


router = APIRouter(
    prefix="/api/health-tips",
    tags=["AI Health Tips"],
)


HEALTH_TIP_CATEGORIES = [
    "general wellness",
    "heart health",
    "diabetes care",
    "weight management",
    "healthy diet",
    "sleep improvement",
    "stress management",
    "hydration",
    "exercise",
    "mental wellness",
]


@router.post(
    "/generate",
    response_model=HealthTipsResponse,
)
def generate_health_tips_endpoint(
    request: HealthTipsRequest,
):
    try:
        return generate_health_tips(request)

    except HealthTipsConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    except HealthTipsServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.get("/categories")
def get_health_tip_categories():
    return {
        "total": len(HEALTH_TIP_CATEGORIES),
        "categories": HEALTH_TIP_CATEGORIES,
    }