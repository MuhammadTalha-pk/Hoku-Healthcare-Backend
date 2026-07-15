from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/health",
    summary="Check API health",
    description="Confirms that the HOKU Health Care backend is running.",
)
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "HOKU Health Care API",
        "version": "0.1.0",
    }