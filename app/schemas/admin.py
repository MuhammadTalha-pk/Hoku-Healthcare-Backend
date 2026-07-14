from pydantic import BaseModel


class AdminDashboardResponse(BaseModel):
    total_services: int
    active_services: int
    total_reviews: int
    approved_reviews: int
    pending_reviews: int
    average_rating: float