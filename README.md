# HOKU Health Care Backend

A collaborative FastAPI backend for the HOKU home-healthcare platform.

**Contributors:** Muhammad Talha (Backend + AI Lead) and Faisal Majeed (Backend + AI).
See [CONTRIBUTORS.md](CONTRIBUTORS.md) for the responsibility map.

## Important repository structure

The project must have only one root application:

```text
Hoku-Healthcare-Backend/
├── app/
├── alembic/
├── tests/
├── postman/
├── scripts/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── render.yaml
└── README.md
```

Do not place another `Hoku-Healthcare-Backend/` directory inside the repository.

## Main features

- PostgreSQL and SQLAlchemy 2
- Alembic migrations for 12 project tables
- Patient, doctor and admin roles
- JWT access/refresh tokens and logout
- Doctor profiles and weekly availability
- Appointment booking and authorization
- Medication reminders with email/SMS delivery
- Scheduled reminder worker
- Services, reviews and admin APIs
- AI chatbot, doctor recommender and health tips
- Profile-picture upload
- CORS, rate limiting and global error handling
- Swagger/OpenAPI, Pytest, Docker and Render configuration

## Local setup

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Open:

- Swagger: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/api/v1/health`

## Tests

```bash
pytest -q
```

## API groups

- `/api/v1/auth`
- `/api/v1/users`
- `/api/v1/doctors`
- `/api/v1/appointments`
- `/api/v1/reminders`
- `/api/v1/services`
- `/api/v1/reviews`
- `/api/v1/admin`
- `/api/v1/ai`
- `/api/v1/files`

External AI endpoints require `OPENROUTER_API_KEY`. Real email/SMS delivery requires
SMTP and Twilio credentials; otherwise `NOTIFICATION_MODE=log` is safe for development.
