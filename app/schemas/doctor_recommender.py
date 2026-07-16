from typing import List

from pydantic import BaseModel, Field, field_validator


class DoctorRecommendationRequest(BaseModel):
    symptoms: List[str] = Field(
        ...,
        min_length=1,
        description="List of symptoms reported by the patient",
        examples=[["fever", "headache", "body pain"]],
    )

    age: int | None = Field(
        default=None,
        ge=0,
        le=120,
        description="Patient age",
    )

    gender: str | None = Field(
        default=None,
        max_length=20,
        description="Patient gender",
    )

    duration_days: int | None = Field(
        default=None,
        ge=0,
        le=365,
        description="How many days the symptoms have continued",
    )

    @field_validator("symptoms")
    @classmethod
    def clean_symptoms(cls, symptoms: List[str]) -> List[str]:
        cleaned = [
            symptom.strip().lower()
            for symptom in symptoms
            if symptom.strip()
        ]

        if not cleaned:
            raise ValueError("At least one valid symptom is required.")

        return cleaned


class DoctorRecommendationResponse(BaseModel):
    recommended_specialty: str
    matched_symptoms: List[str]
    urgency: str
    reason: str
    advice: str
    emergency_warning: str | None = None
    disclaimer: str