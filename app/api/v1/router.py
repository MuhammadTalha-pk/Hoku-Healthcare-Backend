from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    ai_reminder,
    appointments,
    auth,
    chatbot,
    doctor_recommender,
    doctors,
    file_upload,
    health,
    health_tips,
    reminders,
    reviews,
    services,
    users,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(doctors.router, prefix="/doctors", tags=["Doctors"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
api_router.include_router(reminders.router, prefix="/reminders", tags=["Medication Reminders"])
api_router.include_router(services.router, prefix="/services", tags=["Services"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(ai_reminder.router, prefix="/ai", tags=["AI Medication Reminder"])
api_router.include_router(chatbot.router, prefix="/ai", tags=["AI Chatbot"])
api_router.include_router(doctor_recommender.router, prefix="/ai", tags=["AI Doctor Recommender"])
api_router.include_router(health_tips.router, prefix="/ai", tags=["AI Health Tips"])
api_router.include_router(file_upload.router, prefix="/files", tags=["File Upload"])
