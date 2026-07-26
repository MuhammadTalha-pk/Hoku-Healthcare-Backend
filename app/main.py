import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.middleware.cors import add_cors_middleware
from app.middleware.error_handler import add_error_handlers
from app.middleware.rate_limit import add_rate_limit_middleware
from app.workers.reminder_tasks import start_reminder_scheduler, stop_reminder_scheduler

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting %s", settings.APP_NAME)
    start_reminder_scheduler()
    yield
    stop_reminder_scheduler()


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Collaborative HOKU Health Care backend. Muhammad Talha: core FastAPI, PostgreSQL, "
        "authentication, users, doctors, appointments, reminders, email/SMS and deployment. "
        "Faisal Majeed: services, reviews, admin, AI chatbot, doctor recommender, health tips, "
        "file upload, CORS, rate limiting and error handling."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

add_cors_middleware(app)
add_rate_limit_middleware(app)
add_error_handlers(app)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

upload_root = Path("uploads")
upload_root.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_root), name="uploads")


@app.get("/", tags=["Root"])
def root() -> dict[str, str]:
    return {
        "message": f"{settings.APP_NAME} is running",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
    }
