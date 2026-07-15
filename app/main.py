from fastapi import FastAPI

from app.api.v1.router import api_router

app = FastAPI(
    title="HOKU Health Care API",
    description="Backend API for the HOKU home-healthcare platform.",
    version="0.1.0",
)


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    return {
        "message": "HOKU Health Care API is running",
        "documentation": "/docs",
    }


app.include_router(
    api_router,
    prefix="/api/v1",
)