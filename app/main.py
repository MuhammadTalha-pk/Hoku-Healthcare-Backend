from fastapi import FastAPI

from app.database import Base, engine

from app.routers import services, reviews
from app.models import service, review
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hoku Health Care API",
    description="FastAPI backend for Hoku Health Care internship project",
    version="1.0.0"
)

app.include_router(services.router)
app.include_router(reviews.router)

@app.get("/")
def home():
    return {"message": "Hoku Health Care API is running"}