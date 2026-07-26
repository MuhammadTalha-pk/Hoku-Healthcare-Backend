import os
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path

os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///./test_hoku_healthcare.db"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-with-more-than-24-characters"
os.environ["ENABLE_SCHEDULER"] = "false"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ["NOTIFICATION_MODE"] = "log"
os.environ["INTERNAL_API_KEY"] = "test-internal-key"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import Base, SessionLocal, engine
from app.main import app
from app.models.doctor import Doctor
from app.models.doctor_availability import DoctorAvailability
from app.models.service import Service
from app.models.user import User


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def service_id():
    with SessionLocal() as db:
        service = Service(name="Home Health", description="Home nursing service", price=2500, is_active=True)
        db.add(service)
        db.commit()
        db.refresh(service)
        return service.id


def register_patient(client: TestClient, email: str = "patient@example.com", phone: str | None = "+923001234567"):
    response = client.post(
        "/api/v1/auth/register/patient",
        json={
            "full_name": "Test Patient",
            "email": email,
            "phone": phone,
            "address": "Rawalpindi",
            "password": "StrongPass123!",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def register_doctor(client: TestClient, email: str = "doctor@example.com"):
    response = client.post(
        "/api/v1/auth/register/doctor",
        json={
            "full_name": "Dr Test",
            "email": email,
            "phone": "+923009999999",
            "address": "Islamabad",
            "password": "StrongPass123!",
            "specialty": "General Physician",
            "experience_years": 5,
            "qualification": "MBBS",
            "consultation_fee": 2000,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def login(client: TestClient, email: str, password: str = "StrongPass123!"):
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def set_doctor_availability(client: TestClient, doctor_token: str, target_date: date):
    response = client.put(
        "/api/v1/doctors/me/availability",
        headers=auth_header(doctor_token),
        json={
            "slots": [
                {
                    "day_of_week": target_date.strftime("%A"),
                    "start_time": "09:00:00",
                    "end_time": "17:00:00",
                    "is_available": True,
                }
            ]
        },
    )
    assert response.status_code == 200, response.text
    return response.json()

def make_admin(email: str = "admin@example.com") -> None:
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        if user is None:
            raise AssertionError(f"User {email} not found")
        user.role = "admin"
        db.commit()
