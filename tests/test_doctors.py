from datetime import date, timedelta

from tests.conftest import auth_header, login, register_doctor, set_doctor_availability


def test_doctor_profile_and_availability(client):
    register_doctor(client)
    tokens = login(client, "doctor@example.com")
    target = date.today() + timedelta(days=7)

    slots = set_doctor_availability(client, tokens["access_token"], target)
    assert len(slots) == 1
    assert slots[0]["day_of_week"] == target.strftime("%A")

    public_list = client.get("/api/v1/doctors")
    assert public_list.status_code == 200
    assert public_list.json()[0]["availability"][0]["start_time"] == "09:00:00"


def test_overlapping_availability_rejected(client):
    register_doctor(client)
    token = login(client, "doctor@example.com")["access_token"]
    response = client.put(
        "/api/v1/doctors/me/availability",
        headers=auth_header(token),
        json={"slots": [
            {"day_of_week": "Monday", "start_time": "09:00", "end_time": "12:00"},
            {"day_of_week": "Monday", "start_time": "11:00", "end_time": "14:00"},
        ]},
    )
    assert response.status_code == 422
