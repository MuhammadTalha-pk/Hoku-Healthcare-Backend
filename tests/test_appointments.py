from datetime import date, timedelta

from tests.conftest import auth_header, login, register_doctor, register_patient, set_doctor_availability


def setup_booking(client, service_id):
    register_patient(client)
    register_doctor(client)
    patient_token = login(client, "patient@example.com")["access_token"]
    doctor_token = login(client, "doctor@example.com")["access_token"]
    target = date.today() + timedelta(days=7)
    set_doctor_availability(client, doctor_token, target)
    doctor_id = client.get("/api/v1/doctors").json()[0]["id"]
    return patient_token, doctor_token, doctor_id, target


def test_appointment_booking_authorization_and_status(client, service_id):
    patient_token, doctor_token, doctor_id, target = setup_booking(client, service_id)
    payload = {
        "doctor_id": doctor_id,
        "service_id": service_id,
        "appointment_date": target.isoformat(),
        "appointment_time": "10:00:00",
        "notes": "Routine visit",
    }
    booked = client.post("/api/v1/appointments", headers=auth_header(patient_token), json=payload)
    assert booked.status_code == 201, booked.text
    appointment_id = booked.json()["id"]

    duplicate = client.post("/api/v1/appointments", headers=auth_header(patient_token), json=payload)
    assert duplicate.status_code == 409

    confirmed = client.put(
        f"/api/v1/appointments/{appointment_id}/status",
        headers=auth_header(doctor_token),
        json={"status": "confirmed"},
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "confirmed"


def test_past_and_unavailable_bookings_rejected(client, service_id):
    register_patient(client)
    register_doctor(client)
    token = login(client, "patient@example.com")["access_token"]
    doctor_id = client.get("/api/v1/doctors").json()[0]["id"]
    response = client.post(
        "/api/v1/appointments",
        headers=auth_header(token),
        json={
            "doctor_id": doctor_id,
            "service_id": service_id,
            "appointment_date": (date.today() - timedelta(days=1)).isoformat(),
            "appointment_time": "10:00:00",
        },
    )
    assert response.status_code == 400


def test_patient_cannot_read_another_patients_appointment(client, service_id):
    patient_token, _, doctor_id, target = setup_booking(client, service_id)
    booked = client.post(
        "/api/v1/appointments",
        headers=auth_header(patient_token),
        json={
            "doctor_id": doctor_id,
            "service_id": service_id,
            "appointment_date": target.isoformat(),
            "appointment_time": "10:00:00",
        },
    ).json()
    register_patient(client, email="other@example.com", phone="+923001111111")
    other_token = login(client, "other@example.com")["access_token"]
    denied = client.get(f"/api/v1/appointments/{booked['id']}", headers=auth_header(other_token))
    assert denied.status_code == 403
