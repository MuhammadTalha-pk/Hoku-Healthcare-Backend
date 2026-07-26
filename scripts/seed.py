from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.service import Service

DEFAULT_SERVICES = [
    ("Home Health", "Nursing, therapy and medical care at home", 2500),
    ("Palliative Care", "Comfort-focused care for serious illness", 3500),
    ("Hospice Care", "End-of-life care and family support", 4000),
]


def main():
    with SessionLocal() as db:
        for name, description, price in DEFAULT_SERVICES:
            existing = db.scalar(select(Service).where(Service.name == name))
            if not existing:
                db.add(Service(name=name, description=description, price=price, is_active=True))
        db.commit()
    print("Default services seeded successfully")


if __name__ == "__main__":
    main()
