from fastapi import FastAPI

from app.routers import doctor_recommender, health_tips


app = FastAPI(
    title="Hoku Health Care API",
    description="AI Doctor Recommender and AI Health Tips APIs",
    version="1.0.0",
)

app.include_router(doctor_recommender.router)
app.include_router(health_tips.router)


@app.get("/")
def home():
    return {"message": "Hoku Health Care API is running"}