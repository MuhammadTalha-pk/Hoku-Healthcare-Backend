from tests.conftest import auth_header, login, make_admin, register_patient


def setup_admin(client):
    register_patient(client, email="admin@example.com", phone="+923008888888")
    make_admin()
    return login(client, "admin@example.com")["access_token"]


def test_services_admin_crud_and_public_list(client):
    admin_token = setup_admin(client)
    created = client.post(
        "/api/v1/services/",
        headers=auth_header(admin_token),
        json={"name": "Palliative Care", "description": "Comfort care", "price": 3500},
    )
    assert created.status_code == 201, created.text
    public = client.get("/api/v1/services/")
    assert public.status_code == 200
    assert public.json()[0]["name"] == "Palliative Care"


def test_review_create_requires_patient_and_admin_approval(client):
    register_patient(client)
    patient_token = login(client, "patient@example.com")["access_token"]
    created = client.post(
        "/api/v1/reviews/",
        headers=auth_header(patient_token),
        json={"rating": 5, "comment": "Very caring service"},
    )
    assert created.status_code == 201, created.text
    review_id = created.json()["id"]
    assert client.get("/api/v1/reviews/").json() == []

    admin_token = setup_admin(client)
    approved = client.patch(
        f"/api/v1/reviews/{review_id}/approval",
        headers=auth_header(admin_token),
        json={"is_approved": True},
    )
    assert approved.status_code == 200
    assert len(client.get("/api/v1/reviews/").json()) == 1


def test_doctor_recommender_and_health_tip_categories(client):
    register_patient(client)
    token = login(client, "patient@example.com")["access_token"]
    recommendation = client.post(
        "/api/v1/ai/recommend-doctor",
        headers=auth_header(token),
        json={"symptoms": ["chest pain", "shortness of breath"], "duration_days": 1},
    )
    assert recommendation.status_code == 200
    assert recommendation.json()["recommended_specialty"] == "Cardiologist"
    categories = client.get("/api/v1/ai/health-tip-categories")
    assert categories.status_code == 200
    assert categories.json()["total"] >= 5


def test_chatbot_reports_missing_key_safely(client):
    register_patient(client)
    token = login(client, "patient@example.com")["access_token"]
    response = client.post(
        "/api/v1/ai/chat",
        headers=auth_header(token),
        json={"message": "I have a headache"},
    )
    assert response.status_code == 503
