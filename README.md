<div align="center">

# HOKU Health Care Backend

### FastAPI • PostgreSQL • JWT Authentication • Medication Reminders • REST APIs

Backend service for the **HOKU Health Care** home-healthcare platform, developed as a collaborative internship project at **TechNexus Virtual University**.

![Status](https://img.shields.io/badge/Status-In%20Development-orange)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white)

</div>

---

## Project Overview

HOKU Health Care is a home-healthcare platform designed to connect patients, doctors, caregivers and administrators through a secure digital system.

This repository contains the planned backend implementation for:

- User registration and authentication
- Patient and doctor profile management
- Doctor availability
- Appointment booking and status management
- Medication reminders
- Email and SMS notifications
- Role-based access control
- REST API documentation
- Backend deployment

> **Current status:** Initial development and project setup.

---

## Internship Context

This project is being developed during my internship at **TechNexus Virtual University**.

- **Backend Lead:** Muhammad Talha
- **Backend Contributor:** Faisal Majeed
- **Organization:** [TechNexus-VU](https://github.com/TechNexus-VU)

This repository is intended for collaborative development. Each contributor works on a separate feature branch and submits changes through pull requests.

---

## Planned Features

### Authentication and Authorization

- Patient registration
- Doctor registration
- Secure login
- Password hashing with bcrypt
- JWT access tokens
- Role-based authorization
- Protected API routes

### User Management

- View and update personal profile
- Change password
- Patient management
- Doctor management
- Administrator access controls

### Doctor Management

- Doctor profiles
- Specialties and qualifications
- Experience and biography
- Consultation fee
- Availability schedule
- Active and inactive status

### Appointment Management

- Create appointments
- View patient appointments
- View doctor appointments
- Prevent duplicate time-slot bookings
- Confirm, complete or cancel appointments
- Appointment history

### Medication Reminders

- Create medication reminders
- Set medicine name, dosage and time
- Configure frequency and date range
- Enable or disable reminders
- Scheduled reminder processing
- Email and SMS notification support

### API Documentation

- Interactive Swagger documentation
- OpenAPI schema
- Example request and response formats

---

## Technology Stack

| Area | Technology |
|---|---|
| Backend Framework | FastAPI |
| Programming Language | Python |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Authentication | JWT and bcrypt |
| Database Migrations | Alembic |
| Email Notifications | SMTP or SendGrid |
| SMS Notifications | Twilio |
| Background Jobs | APScheduler, Celery or cron |
| Testing | Pytest |
| API Documentation | Swagger / OpenAPI |
| Deployment | Render |
| Containerization | Docker |

---

## Planned Project Structure

```text
hoku-healthcare-backend/
│
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   └── dependencies.py
│   ├── models/
│   │   ├── user.py
│   │   ├── doctor.py
│   │   ├── appointment.py
│   │   ├── reminder.py
│   │   ├── service.py
│   │   └── notification.py
│   ├── schemas/
│   │   ├── user_schema.py
│   │   ├── doctor_schema.py
│   │   ├── appointment_schema.py
│   │   └── reminder_schema.py
│   ├── api/
│   │   └── v1/
│   │       ├── router.py
│   │       └── endpoints/
│   │           ├── auth.py
│   │           ├── users.py
│   │           ├── doctors.py
│   │           ├── appointments.py
│   │           ├── reminders.py
│   │           ├── services.py
│   │           └── admin.py
│   ├── services/
│   │   ├── email_service.py
│   │   ├── sms_service.py
│   │   └── reminder_service.py
│   └── workers/
│       └── reminder_tasks.py
├── alembic/
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Planned API Endpoints

### Health Check

```http
GET /health
```

### Authentication

```http
POST /api/v1/auth/register/patient
POST /api/v1/auth/register/doctor
POST /api/v1/auth/login
POST /api/v1/auth/refresh
```

### Users

```http
GET /api/v1/users/me
PUT /api/v1/users/me
PUT /api/v1/users/me/password
```

### Doctors

```http
GET /api/v1/doctors
GET /api/v1/doctors/{doctor_id}
GET /api/v1/doctors/specialty/{specialty}
PUT /api/v1/doctors/me
PUT /api/v1/doctors/me/availability
```

### Appointments

```http
POST /api/v1/appointments
GET /api/v1/appointments/patient
GET /api/v1/appointments/doctor
GET /api/v1/appointments/{appointment_id}
PUT /api/v1/appointments/{appointment_id}/status
PUT /api/v1/appointments/{appointment_id}/cancel
```

### Medication Reminders

```http
POST /api/v1/reminders
GET /api/v1/reminders
GET /api/v1/reminders/{reminder_id}
PUT /api/v1/reminders/{reminder_id}
DELETE /api/v1/reminders/{reminder_id}
```

---

## Authentication Format

Protected routes will use a Bearer token:

```http
Authorization: Bearer <access_token>
```

Example login response:

```json
{
  "access_token": "jwt-access-token",
  "refresh_token": "jwt-refresh-token",
  "token_type": "bearer"
}
```

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/MuhammadTalha-pk/hoku-healthcare-backend.git
cd hoku-healthcare-backend
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Activate it on macOS or Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file from `.env.example`.

```env
APP_NAME=HOKU Health Care API
APP_ENV=development
DEBUG=true

DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/hoku_healthcare

JWT_SECRET_KEY=replace-with-a-secure-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

SMTP_HOST=
SMTP_PORT=
SMTP_USERNAME=
SMTP_PASSWORD=
EMAIL_FROM=

TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
```

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the API

```bash
uvicorn app.main:app --reload
```

### 7. Open the documentation

```text
Swagger UI: http://127.0.0.1:8000/docs
ReDoc:      http://127.0.0.1:8000/redoc
```

---

## Collaboration Workflow

The repository uses the following branches:

```text
main
develop
feature/muhammad-talha-backend-core
feature/faisal-services-admin
```

Recommended workflow:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

After completing work:

```bash
git add .
git commit -m "feat: describe the completed feature"
git push -u origin feature/your-feature-name
```

Then open a pull request:

```text
feature/your-feature-name → develop
```

Stable and tested work will later be merged:

```text
develop → main
```

---

## Security

Never commit sensitive information such as:

- `.env` files
- Database passwords
- JWT secrets
- SMTP credentials
- Twilio credentials
- API keys
- Real patient information
- Medical records
- Private client data

Use environment variables and test data only.

---

## Contributors

### Muhammad Talha

**Backend Lead**

Planned responsibilities:

- FastAPI project foundation
- PostgreSQL configuration
- Authentication and authorization
- Users and doctors APIs
- Appointments API
- Medication reminders
- Email and SMS services
- Background reminder jobs
- Deployment and Swagger documentation

- GitHub: [MuhammadTalha-pk](https://github.com/MuhammadTalha-pk)
- LinkedIn: [muhammadtalha-pk](https://www.linkedin.com/in/muhammadtalha-pk/)

### Faisal Majeed

**Backend Contributor**

Planned responsibilities include services, reviews, administration and related backend modules.

---

## License

This repository currently has **no open-source license**. The code may not be copied, redistributed or reused without permission from the project owner and internship organization.

---

<div align="center">

### Building a secure and reliable backend for digital home healthcare.

</div>
