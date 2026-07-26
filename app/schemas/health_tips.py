from pydantic import BaseModel, Field, field_validator


class HealthTipsRequest(BaseModel):
    category: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["heart health"],
    )

    age: int | None = Field(
        default=None,
        ge=0,
        le=120,
    )

    gender: str | None = Field(
        default=None,
        max_length=20,
    )

    medical_condition: str | None = Field(
        default=None,
        max_length=200,
        examples=["high blood pressure"],
    )

    @field_validator("category")
    @classmethod
    def clean_category(cls, value: str) -> str:
        cleaned = value.strip().lower()

        if not cleaned:
            raise ValueError("Health tip category is required.")

        return cleaned


class HealthTipsResponse(BaseModel):
    category: str
    tips: list[str]
    daily_habits: list[str]
    things_to_avoid: list[str]
    doctor_advice: str
    disclaimer: str