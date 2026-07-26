<div align="center">

# HOKU Health Care Backend

### FastAPI • PostgreSQL • JWT Authentication • Appointment Management • Medication Reminders • AI APIs

A complete REST API for the **HOKU Health Care** home-healthcare platform, developed as a collaborative internship project at **TechNexus Virtual University**.

![Status](https://img.shields.io/badge/Backend-Complete-2ea44f)
![Tests](https://img.shields.io/badge/Tests-15%20Passed-2ea44f)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)

[API Documentation](#api-documentation) • [Local Setup](#local-development-setup) • [Docker Setup](#run-with-docker) • [Contributors](#contributors)

</div>

---

## Project Overview

HOKU Health Care is a backend platform for managing digital home-healthcare services. It provides secure APIs for patients, doctors and administrators and combines appointment booking, doctor availability, medication reminders, healthcare services, reviews, notifications and selected AI-assisted features in one FastAPI application.

The backend has been fully integrated into a single root application. It contains the work of **Muhammad Talha** and **Faisal Majeed**, uses one shared PostgreSQL database, one JWT authentication system and one versioned API router.

### Current Status

| Area | Status |
|---|---|
| FastAPI application | Complete |
| PostgreSQL schema | Complete |
| Alembic migration | Complete |
| Authentication and role authorization | Complete |
| Doctors and availability | Complete |
| Appointment management | Complete |
| Medication reminders | Complete |
| Email/SMS integration | Implemented; credentials required for live delivery |
| Services, reviews and admin APIs | Complete |
| AI chatbot and health tips | Implemented; OpenRouter key required |
| Automated tests | 15 passing |
| Swagger/OpenAPI | Available |
| Docker and Render configuration | Included |

> The application is complete for local development and integration. Live SMTP, Twilio, OpenRouter and Render functionality requires account credentials supplied through environment variables.

---

## Main User Roles

### Patient

Patients can register, log in, manage their profiles, browse doctors and services, book appointments, view appointment history, create medication reminders, upload profile pictures and submit reviews.

### Doctor

Doctors can register with professional details, manage their profiles, define weekly availability, view assigned appointments and update appointment statuses.

### Administrator

Administrators can view platform statistics, manage users, manage healthcare services, review appointments and approve or reject patient reviews.

> There is no public administrator-registration endpoint. An administrator role should be assigned only to a trusted existing user directly in the database.

---

## Implemented Features

### Authentication and Security

- Patient and doctor registration
- JSON and OAuth2 form login
- Password hashing with bcrypt
- JWT access and refresh tokens
- Access-token and refresh-token separation
- Refresh-token rotation/version validation
- Secure logout and token revocation
- Password reset request and confirmation
- Role-based dependencies for patient, doctor and administrator access
- Configurable CORS
- Per-process in-memory rate limiting
- Centralized API error responses
- Environment-based secret management

### Doctor Management

- Public doctor directory
- Specialty filtering
- Doctor profile details
- Qualifications, experience, biography and consultation fee
- Active/available status
- Weekly availability schedules
- Overlapping-slot validation

### Appointment Management

- Patient appointment booking
- Future-date validation
- Active service validation
- Doctor availability validation
- Duplicate doctor-slot prevention
- Patient schedule-conflict prevention
- Patient and doctor appointment lists
- Ownership-based appointment access
- Controlled appointment status transitions
- 24-hour patient cancellation policy
- Cancellation reason storage

### Medication Reminders

- Create, read, update and delete reminders
- Daily, twice-daily, weekly and monthly frequencies
- Time-zone-aware scheduling
- Optional start and end dates
- Automatic next-run calculation
- Background reminder worker
- Manual internal reminder-delivery endpoint
- Development log mode
- Live SMTP email support
- Live Twilio SMS support

### Healthcare Services and Reviews

- Public list of active healthcare services
- Administrator service CRUD operations
- Soft deletion of services to preserve appointment history
- Patient review submission
- Public display of approved reviews only
- Review editing and deletion by the owner
- Administrator approval and rejection workflow

### Administration

- Total users, patients and doctors
- Appointment and service counts
- Active service statistics
- Review totals, pending reviews and average rating
- User activation and deactivation
- Administrator views for all services and reviews

### AI and Additional Modules

- Authenticated HOKU health chatbot
- Rule-based doctor-specialty recommender
- AI-generated health tips
- Health-tip categories
- Public doctor-specialty list
- Profile-picture uploads for JPG, PNG and WEBP files
- Maximum image size of 5 MB
- Static serving of uploaded profile pictures

> AI output is for general guidance only and must not be treated as a medical diagnosis.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Web framework | FastAPI |
| API server | Uvicorn |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2 |
| PostgreSQL driver | Psycopg 3 |
| Validation/settings | Pydantic 2 and pydantic-settings |
| Authentication | PyJWT and bcrypt |
| Migrations | Alembic |
| Testing | Pytest and FastAPI TestClient |
| AI provider | OpenRouter through an OpenAI-compatible client |
| Email | SMTP |
| SMS | Twilio REST API |
| Background processing | Application-managed reminder worker |
| Containerization | Docker and Docker Compose |
| Deployment | Render Blueprint |
| API documentation | Swagger UI, ReDoc and OpenAPI |

---

## System Architecture

```text
Client Applications
        │
        ▼
FastAPI REST API
        │
        ├── Authentication and role dependencies
        ├── Users, doctors and availability
        ├── Appointments and services
        ├── Medication reminders
        ├── Reviews and administration
        ├── AI and file-upload modules
        └── CORS, rate limiting and error handling
        │
        ▼
SQLAlchemy ORM
        │
        ▼
PostgreSQL Database

External integrations:
SMTP • Twilio • OpenRouter • Render
```

---

## Database Schema

The initial Alembic migration creates the following 12 project tables:

| Table | Purpose |
|---|---|
| `users` | Patient, doctor and administrator accounts |
| `doctors` | Doctor professional profiles |
| `doctor_availability` | Weekly doctor time slots |
| `services` | Home-healthcare services |
| `appointments` | Patient bookings and appointment statuses |
| `reminders` | Medication schedules and delivery state |
| `reviews` | Patient feedback and approval status |
| `chat_history` | AI conversation records |
| `symptoms` | Symptom and specialist reference data |
| `notifications` | User alerts and delivery records |
| `blog_posts` | Healthcare content records |
| `health_tips` | Stored wellness tips |

Alembic also creates its own `alembic_version` table for migration tracking.

---

## Repository Structure

```text
Hoku-Healthcare-Backend/
│
├── app/
│   ├── main.py
│   ├── api/v1/
│   │   ├── router.py
│   │   └── endpoints/
│   │       ├── admin.py
│   │       ├── ai_reminder.py
│   │       ├── appointments.py
│   │       ├── auth.py
│   │       ├── chatbot.py
│   │       ├── doctor_recommender.py
│   │       ├── doctors.py
│   │       ├── file_upload.py
│   │       ├── health.py
│   │       ├── health_tips.py
│   │       ├── reminders.py
│   │       ├── reviews.py
│   │       ├── services.py
│   │       └── users.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   └── security.py
│   ├── middleware/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   └── workers/
│
├── alembic/
├── postman/
├── scripts/
├── tests/
├── uploads/profile_pictures/
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── render.yaml
├── requirements.txt
├── start.sh
├── CONTRIBUTORS.md
└── README.md
```

> Keep `app/` directly in the repository root. Do not place another backend folder around it.

---

## API Documentation

After starting the server, open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
- Health check: `http://127.0.0.1:8000/api/v1/health`

The application exposes **44 documented API paths** across the following modules.

### Health

| Method | Path | Access |
|---|---|---|
| GET | `/api/v1/health` | Public |

### Authentication

| Method | Path | Access |
|---|---|---|
| POST | `/api/v1/auth/register/patient` | Public |
| POST | `/api/v1/auth/register/doctor` | Public |
| POST | `/api/v1/auth/login` | Public |
| POST | `/api/v1/auth/token` | Public, OAuth2 form |
| POST | `/api/v1/auth/refresh` | Refresh token |
| POST | `/api/v1/auth/logout` | Authenticated |
| POST | `/api/v1/auth/password-reset/request` | Public |
| POST | `/api/v1/auth/password-reset/confirm` | Reset token |

### Users

| Method | Path | Access |
|---|---|---|
| GET | `/api/v1/users/me` | Authenticated |
| PUT | `/api/v1/users/me` | Authenticated |
| PUT | `/api/v1/users/me/password` | Authenticated |
| GET | `/api/v1/users/patients` | Administrator |
| GET | `/api/v1/users/{user_id}` | Administrator |
| PATCH | `/api/v1/users/{user_id}/active` | Administrator |

### Doctors

| Method | Path | Access |
|---|---|---|
| GET | `/api/v1/doctors` | Public |
| GET | `/api/v1/doctors/{doctor_id}` | Public |
| GET | `/api/v1/doctors/specialty/{specialty}` | Public |
| GET | `/api/v1/doctors/me` | Doctor/administrator |
| PUT | `/api/v1/doctors/me` | Doctor/administrator |
| GET | `/api/v1/doctors/me/availability` | Doctor/administrator |
| PUT | `/api/v1/doctors/me/availability` | Doctor/administrator |

### Appointments

| Method | Path | Access |
|---|---|---|
| POST | `/api/v1/appointments` | Patient |
| GET | `/api/v1/appointments/patient` | Patient |
| GET | `/api/v1/appointments/doctor` | Doctor/administrator |
| GET | `/api/v1/appointments/{appointment_id}` | Owner/assigned doctor/administrator |
| PUT | `/api/v1/appointments/{appointment_id}/status` | Assigned doctor/administrator |
| PUT | `/api/v1/appointments/{appointment_id}/cancel` | Patient owner |

### Medication Reminders

| Method | Path | Access |
|---|---|---|
| POST | `/api/v1/reminders` | Patient |
| GET | `/api/v1/reminders` | Patient |
| GET | `/api/v1/reminders/{reminder_id}` | Patient owner |
| PUT | `/api/v1/reminders/{reminder_id}` | Patient owner |
| DELETE | `/api/v1/reminders/{reminder_id}` | Patient owner |
| POST | `/api/v1/ai/reminder/send` | Internal API key |

### Services

| Method | Path | Access |
|---|---|---|
| GET | `/api/v1/services` | Public |
| GET | `/api/v1/services/{service_id}` | Public |
| POST | `/api/v1/services` | Administrator |
| PUT | `/api/v1/services/{service_id}` | Administrator |
| DELETE | `/api/v1/services/{service_id}` | Administrator |

### Reviews

| Method | Path | Access |
|---|---|---|
| GET | `/api/v1/reviews` | Public, approved reviews only |
| GET | `/api/v1/reviews/{review_id}` | Public, approved review only |
| POST | `/api/v1/reviews` | Patient |
| PUT | `/api/v1/reviews/{review_id}` | Owner/administrator |
| PATCH | `/api/v1/reviews/{review_id}/approval` | Administrator |
| DELETE | `/api/v1/reviews/{review_id}` | Owner/administrator |

### Administration

| Method | Path | Access |
|---|---|---|
| GET | `/api/v1/admin/dashboard` | Administrator |
| GET | `/api/v1/admin/services` | Administrator |
| GET | `/api/v1/admin/reviews` | Administrator |
| GET | `/api/v1/admin/reviews/pending` | Administrator |

### AI and File Upload

| Method | Path | Access |
|---|---|---|
| POST | `/api/v1/ai/chat` | Authenticated; OpenRouter key required |
| POST | `/api/v1/ai/recommend-doctor` | Authenticated |
| GET | `/api/v1/ai/doctor-specialties` | Public |
| POST | `/api/v1/ai/health-tips` | Public; OpenRouter key required |
| GET | `/api/v1/ai/health-tip-categories` | Public |
| POST | `/api/v1/files/profile-picture` | Authenticated |

---

## Authentication

Protected routes use a Bearer access token:

```http
Authorization: Bearer <access_token>
```

Example login request:

```http
POST /api/v1/auth/login
Content-Type: application/json
```

```json
{
  "email": "patient@example.com",
  "password": "StrongPassword123!"
}
```

Example token response:

```json
{
  "access_token": "<jwt-access-token>",
  "refresh_token": "<jwt-refresh-token>",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "full_name": "Example Patient",
    "email": "patient@example.com",
    "role": "patient"
  }
}
```

Refresh tokens cannot be used as access tokens. Changing a password, logging out or deactivating an account invalidates existing tokens through token-version checks.

---

## Local Development Setup

### Prerequisites

Install:

- Python 3.11 or later
- PostgreSQL 14 or later
- Git

### 1. Clone the repository

```bash
git clone https://github.com/MuhammadTalha-pk/Hoku-Healthcare-Backend.git
cd Hoku-Healthcare-Backend
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create the PostgreSQL database

Using `psql`:

```bash
psql -U postgres -h localhost -c "CREATE DATABASE hoku_healthcare;"
```

Alternatively, create a database named `hoku_healthcare` through pgAdmin.

### 5. Configure environment variables

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Update the database username and password in `.env`:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/hoku_healthcare
```

Generate secure application keys before deployment:

```env
JWT_SECRET_KEY=replace-with-a-long-random-secret-at-least-24-characters
INTERNAL_API_KEY=replace-with-a-private-internal-key
```

### 6. Apply database migrations

```bash
alembic upgrade head
```

### 7. Seed default healthcare services

```bash
python -m scripts.seed
```

Expected output:

```text
Default services seeded successfully
```

### 8. Run the test suite

```bash
pytest -q
```

Expected result:

```text
15 passed
```

A Starlette TestClient deprecation warning may appear depending on installed dependency versions. It does not cause test failure.

### 9. Start the API

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

---

## Run with Docker

### 1. Create the environment file

```bash
cp .env.example .env
```

On PowerShell:

```powershell
Copy-Item .env.example .env
```

### 2. Start PostgreSQL and the API

```bash
docker compose up --build
```

Docker Compose creates:

- PostgreSQL on `localhost:5432`
- FastAPI on `localhost:8000`
- A persistent PostgreSQL volume

Open `http://127.0.0.1:8000/docs` after both containers are healthy.

Stop the containers with:

```bash
docker compose down
```

To remove the local database volume as well:

```bash
docker compose down -v
```

---

## Environment Variables

| Variable | Purpose | Development default |
|---|---|---|
| `APP_NAME` | API display name | `HOKU Health Care API` |
| `APP_ENV` | `development`, `test` or `production` | `development` |
| `DEBUG` | Debug logging | `false` |
| `API_V1_PREFIX` | Versioned API prefix | `/api/v1` |
| `DATABASE_URL` | SQLAlchemy database connection | PostgreSQL URL in `.env.example` |
| `JWT_SECRET_KEY` | JWT signing key | Must be replaced |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access-token lifetime | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh-token lifetime | `7` |
| `CORS_ORIGINS` | Comma-separated frontend origins | Local React/Vite origins |
| `RATE_LIMIT_ENABLED` | Enables rate limiting | `true` |
| `RATE_LIMIT_REQUESTS` | Requests allowed per window | `120` |
| `RATE_LIMIT_WINDOW_SECONDS` | Rate-limit window | `60` |
| `ENABLE_SCHEDULER` | Starts reminder worker | `true` |
| `REMINDER_CHECK_INTERVAL_SECONDS` | Reminder polling interval | `1800` |
| `DEFAULT_TIMEZONE` | Default schedule timezone | `Asia/Karachi` |
| `INTERNAL_API_KEY` | Protects manual reminder delivery | Must be replaced |
| `NOTIFICATION_MODE` | `log` or `live` | `log` |
| `SMTP_*` | Live email settings | Empty |
| `TWILIO_*` | Live SMS settings | Empty |
| `OPENROUTER_API_KEY` | AI chatbot/health-tip provider key | Empty |
| `OPENROUTER_MODEL` | OpenRouter model identifier | `openrouter/free` |

### Notification modes

```env
NOTIFICATION_MODE=log
```

`log` mode records reminder deliveries in application logs and is safe for development.

```env
NOTIFICATION_MODE=live
```

`live` mode sends real SMTP email and Twilio SMS messages. Configure all required provider credentials before enabling it.

---

## Creating an Administrator

For security, administrator registration is not public. Register a normal user first, then update the role from PostgreSQL:

```sql
UPDATE users
SET role = 'admin'
WHERE email = 'admin@example.com';
```

Log in again after changing the role so that the application returns the updated account information.

---

## Testing and Verification

The current test suite covers:

- Patient registration, login, refresh and logout
- Access/refresh token separation
- Doctor registration without a manual user ID
- Doctor profile and availability management
- Overlapping availability rejection
- Appointment booking and duplicate-slot prevention
- Past/unavailable appointment rejection
- Appointment ownership authorization
- Doctor appointment status updates
- Medication reminder CRUD
- Manual reminder delivery
- Reminder frequency validation
- Background reminder processing
- Service administration and public listing
- Review approval workflow
- Doctor recommender
- Health-tip categories
- Safe AI configuration errors
- Health check and OpenAPI generation

Run:

```bash
pytest -q
```

Verified project results:

```text
15 tests passed
Python compilation passed
Alembic migration passed
12 project database tables created
OpenAPI generation passed
44 API paths documented
```

---

## Postman Collection

Import the following file into Postman:

```text
postman/HOKU-Integrated-Backend.postman_collection.json
```

Set the base URL to:

```text
http://127.0.0.1:8000
```

Use login endpoints to obtain an access token, then add it as a Bearer token for protected requests.

---

## Render Deployment

A Render Blueprint is included in `render.yaml`.

The deployment configuration creates:

- A Docker-based FastAPI web service
- A PostgreSQL database
- Generated JWT and internal API keys
- Automatic migrations through `start.sh`
- Health checks at `/api/v1/health`

Before deployment, configure:

- `CORS_ORIGINS`
- SMTP variables for live email
- Twilio variables for live SMS
- `OPENROUTER_API_KEY` for AI endpoints
- `NOTIFICATION_MODE=live` only when notification credentials are ready

The production start command runs migrations and starts one Uvicorn worker:

```bash
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1
```

One worker is intentional because the current reminder scheduler runs inside the application process. Running multiple workers would start multiple reminder threads.

---

## Collaboration Workflow

The clean repository currently uses `main` as its primary branch. For future development, use short-lived feature branches:

```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

After completing and testing the change:

```bash
git add -A
git commit -m "feat: describe the completed change"
git push -u origin feature/your-feature-name
```

Open a pull request:

```text
feature/your-feature-name → main
```

Do not place a second copy of the backend inside the repository.

---

## Contributors

### Muhammad Talha — Backend + AI Lead

Responsibilities:

- FastAPI application structure and configuration
- PostgreSQL database integration
- SQLAlchemy models and Alembic migration
- JWT authentication, refresh, logout and password reset
- Users API
- Doctors API and availability
- Appointments API
- Medication reminders API
- SMTP and Twilio reminder delivery
- Background medication-reminder scheduler
- Docker, Render, tests and Postman collection

- GitHub: [MuhammadTalha-pk](https://github.com/MuhammadTalha-pk)
- LinkedIn: [muhammadtalha-pk](https://www.linkedin.com/in/muhammadtalha-pk/)

### Faisal Majeed — Backend + AI Contributor

Responsibilities:

- Services API
- Reviews API
- Admin dashboard API
- AI chatbot and OpenRouter integration
- Doctor recommender
- AI health tips
- Profile-picture upload
- CORS configuration
- Rate limiting
- Global error handling

The modules were integrated into one shared FastAPI, PostgreSQL and JWT architecture. See [`CONTRIBUTORS.md`](CONTRIBUTORS.md) for the responsibility map.

---

## Security and Privacy

Never commit:

- `.env` files
- Database passwords
- JWT or internal API keys
- SMTP credentials
- Twilio credentials
- OpenRouter/API keys
- Real patient information
- Medical records
- Private client data

Use test data during development. Rotate any credential immediately if it is accidentally committed.

This project provides software infrastructure and general health-information features. It is **not a medical device**, does not provide a clinical diagnosis and should not replace advice from a qualified healthcare professional.

---

## Known Production Considerations

Before high-traffic production use:

- Replace the in-memory rate limiter with Redis or another shared store.
- Move reminder scheduling to a dedicated worker/queue if multiple API instances are required.
- Use cloud/object storage instead of the local `uploads/` directory.
- Add structured monitoring, audit logs and provider-delivery webhooks.
- Add broader integration, load and security testing.
- Review healthcare-data and privacy compliance requirements for the deployment country.

---

## License

This repository currently has **no open-source license**. The code may not be copied, redistributed or reused without permission from the project owner and the internship organization.

---

<div align="center">

### Building a secure, testable and reliable backend for digital home healthcare.

</div>
