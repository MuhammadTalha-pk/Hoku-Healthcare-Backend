from tests.conftest import auth_header, login, register_doctor, register_patient


def test_patient_registration_login_refresh_and_logout(client):
    user = register_patient(client)
    assert user["role"] == "patient"

    tokens = login(client, "patient@example.com")
    profile = client.get("/api/v1/users/me", headers=auth_header(tokens["access_token"]))
    assert profile.status_code == 200

    # A refresh token must never work as an access token.
    rejected = client.get("/api/v1/users/me", headers=auth_header(tokens["refresh_token"]))
    assert rejected.status_code == 401

    refreshed = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refreshed.status_code == 200

    logout = client.post("/api/v1/auth/logout", headers=auth_header(tokens["access_token"]))
    assert logout.status_code == 200
    invalid_after_logout = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert invalid_after_logout.status_code == 401


def test_doctor_registration_does_not_require_user_id(client):
    user = register_doctor(client)
    assert user["role"] == "doctor"
    tokens = login(client, "doctor@example.com")
    profile = client.get("/api/v1/doctors/me", headers=auth_header(tokens["access_token"]))
    assert profile.status_code == 200
    assert profile.json()["specialty"] == "General Physician"
