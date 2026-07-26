# Contributor Responsibility Map

## Muhammad Talha — Backend + AI Lead

- FastAPI application structure and configuration
- PostgreSQL database and Alembic migration
- JWT authentication, refresh and logout
- Users API
- Doctors API and availability
- Appointments API
- Medication reminders API
- SMTP/Twilio reminder delivery
- Background medication-reminder scheduler
- Docker, Render configuration, tests and Postman collection

## Faisal Majeed — Backend + AI Contributor

- Services API
- Reviews API
- Admin API/dashboard
- AI chatbot and OpenRouter integration
- AI doctor recommender
- AI health tips
- Profile-picture upload
- CORS configuration
- Rate limiting
- Global error handling

During integration, Faisal's modules were moved from `app/routers/` into the shared
`app/api/v1/endpoints/` architecture and updated to use the common PostgreSQL models,
database session and JWT role dependencies. This is a structural integration, not a
claim that the original module logic was written by another contributor.
