from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    admin,
    chatbot,
    doctor_recommender,
    file_upload,
    health_tips,
    reviews,
    services,
)

app = FastAPI(
    title="Hoku Health Care API",
    description="Backend APIs for Hoku Health Care",
    version="1.0.0",
)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "status_code": exc.status_code,
            "message": exc.detail,
            "path": request.url.path,
        },
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "status_code": 422,
            "message": "Invalid request data",
            "path": request.url.path,
            "errors": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    print(f"Unexpected error: {repr(exc)}")

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "status_code": 500,
            "message": "Internal server error",
            "path": request.url.path,
        },
    )
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["20/minute"],
)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)
app.add_middleware(SlowAPIMiddleware)
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(services.router)
app.include_router(reviews.router)
app.include_router(admin.router)
app.include_router(chatbot.router)
app.include_router(doctor_recommender.router)
app.include_router(health_tips.router)
app.include_router(file_upload.router)


@app.get("/", tags=["Root"])
def home():
    return {
        "message": "Hoku Health Care API is running",
        "cors": "enabled",
    }
