"""Admin dashboard schemas. Original contributor: Faisal Majeed."""

from pydantic import BaseModel


class AdminDashboardResponse(BaseModel):
    total_users: int
    total_patients: int
    total_doctors: int
    total_appointments: int
    total_services: int
    active_services: int
    total_reviews: int
    approved_reviews: int
    pending_reviews: int
    average_rating: float
