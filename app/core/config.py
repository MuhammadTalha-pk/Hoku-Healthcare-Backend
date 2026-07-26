from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "HOKU Health Care API"
    APP_ENV: Literal["development", "test", "production"] = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # SQLite makes the repository runnable immediately. Production should use PostgreSQL.
    DATABASE_URL: str = "sqlite:///./hoku_healthcare.db"

    JWT_SECRET_KEY: str = "development-only-change-this-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_EXPIRE_MINUTES: int = 30

    CORS_ORIGINS: str = (
        "http://localhost:3000,http://localhost:5173,"
        "http://127.0.0.1:3000,http://127.0.0.1:5173"
    )

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 120
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    ENABLE_SCHEDULER: bool = True
    REMINDER_CHECK_INTERVAL_SECONDS: int = 1800
    REMINDER_RETRY_MINUTES: int = 15
    DEFAULT_TIMEZONE: str = "Asia/Karachi"
    INTERNAL_API_KEY: str = "development-internal-key-change-me"

    # log = safe local development; live = SMTP/Twilio delivery.
    NOTIFICATION_MODE: Literal["log", "live"] = "log"

    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_USE_TLS: bool = True
    EMAIL_FROM: str = "no-reply@hokuhealthcare.local"

    TWILIO_ACCOUNT_SID: str | None = None
    TWILIO_AUTH_TOKEN: str | None = None
    TWILIO_PHONE_NUMBER: str | None = None

    # Faisal Majeed AI integration settings (OpenRouter via OpenAI-compatible API).
    OPENROUTER_API_KEY: str | None = None
    OPENROUTER_MODEL: str = "openrouter/free"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_SITE_URL: str = "http://127.0.0.1:8000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        # Render and some providers return postgres:// or postgresql:// URLs.
        # Explicitly select psycopg 3, which is installed by requirements.txt.
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if value.startswith("postgresql://") and "+psycopg" not in value:
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_secret(cls, value: str) -> str:
        if len(value) < 24:
            raise ValueError("JWT_SECRET_KEY must contain at least 24 characters")
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
