from datetime import date, timedelta

from tests.conftest import auth_header, login, register_patient


def test_reminder_crud_and_manual_delivery(client):
    register_patient(client)
    token = login(client, "patient@example.com")["access_token"]
    created = client.post(
        "/api/v1/reminders",
        headers=auth_header(token),
        json={
            "medicine_name": "Paracetamol",
            "dosage": "500 mg",
            "reminder_time": "08:00:00",
            "frequency": "daily",
            "timezone": "Asia/Karachi",
            "start_date": (date.today() + timedelta(days=1)).isoformat(),
        },
    )
    assert created.status_code == 201, created.text
    reminder = created.json()
    assert reminder["next_run_at"] is not None

    listed = client.get("/api/v1/reminders", headers=auth_header(token))
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    delivered = client.post(
        "/api/v1/ai/reminder/send",
        headers={"X-Internal-API-Key": "test-internal-key"},
        json={"reminder_id": reminder["id"]},
    )
    assert delivered.status_code == 200, delivered.text
    assert delivered.json()["email_sent"] is True

    deleted = client.delete(f"/api/v1/reminders/{reminder['id']}", headers=auth_header(token))
    assert deleted.status_code == 200


def test_twice_daily_requires_second_time(client):
    register_patient(client)
    token = login(client, "patient@example.com")["access_token"]
    response = client.post(
        "/api/v1/reminders",
        headers=auth_header(token),
        json={
            "medicine_name": "Antibiotic",
            "reminder_time": "08:00:00",
            "frequency": "twice_daily",
            "timezone": "Asia/Karachi",
        },
    )
    assert response.status_code == 422


def test_due_reminder_worker_processes_sqlite_datetime(client):
    from datetime import UTC, datetime, timedelta

    from app.core.database import SessionLocal
    from app.models.reminder import Reminder
    from app.services.reminder_service import process_due_reminders

    register_patient(client, email="worker@example.com", phone=None)
    token = login(client, "worker@example.com")["access_token"]
    created = client.post(
        "/api/v1/reminders",
        headers=auth_header(token),
        json={
            "medicine_name": "Vitamin D",
            "reminder_time": "09:00:00",
            "frequency": "daily",
            "timezone": "Asia/Karachi",
        },
    ).json()

    with SessionLocal() as db:
        reminder = db.get(Reminder, created["id"])
        reminder.next_run_at = datetime.now(UTC) - timedelta(minutes=1)
        db.commit()

    with SessionLocal() as db:
        results = process_due_reminders(db)
        assert len(results) == 1
        assert results[0].status == "sent"
