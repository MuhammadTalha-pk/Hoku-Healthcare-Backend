from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.core.dependencies import get_current_doctor
from app.models.doctor import Doctor
from app.models.doctor_availability import DoctorAvailability
from app.models.user import User
from app.schemas.doctor_schema import AvailabilityReplace, AvailabilityResponse, DoctorResponse, DoctorUpdate

router = APIRouter()


def _doctor_query():
    return select(Doctor).options(selectinload(Doctor.user), selectinload(Doctor.availability))


def _profile_for_user(db: Session, user: User) -> Doctor:
    doctor = db.scalar(_doctor_query().where(Doctor.user_id == user.id))
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    return doctor


@router.get("/", response_model=list[DoctorResponse])
def list_doctors(
    specialty: str | None = Query(default=None),
    available_only: bool = Query(default=True),
    db: Session = Depends(get_db),
) -> list[Doctor]:
    statement = _doctor_query().join(Doctor.user).where(User.is_active.is_(True))
    if specialty:
        statement = statement.where(func.lower(Doctor.specialty).contains(specialty.strip().lower()))
    if available_only:
        statement = statement.where(Doctor.is_available.is_(True))
    return list(db.scalars(statement.order_by(User.full_name)).unique().all())


@router.get("/me", response_model=DoctorResponse)
def get_my_doctor_profile(
    current_user: User = Depends(get_current_doctor), db: Session = Depends(get_db)
) -> Doctor:
    return _profile_for_user(db, current_user)


@router.put("/me", response_model=DoctorResponse)
def update_my_doctor_profile(
    payload: DoctorUpdate,
    current_user: User = Depends(get_current_doctor),
    db: Session = Depends(get_db),
) -> Doctor:
    doctor = _profile_for_user(db, current_user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(doctor, field, value)
    db.commit()
    return _profile_for_user(db, current_user)


@router.get("/me/availability", response_model=list[AvailabilityResponse])
def get_my_availability(
    current_user: User = Depends(get_current_doctor), db: Session = Depends(get_db)
) -> list[DoctorAvailability]:
    return _profile_for_user(db, current_user).availability


@router.put("/me/availability", response_model=list[AvailabilityResponse])
def replace_my_availability(
    payload: AvailabilityReplace,
    current_user: User = Depends(get_current_doctor),
    db: Session = Depends(get_db),
) -> list[DoctorAvailability]:
    doctor = _profile_for_user(db, current_user)
    db.execute(delete(DoctorAvailability).where(DoctorAvailability.doctor_id == doctor.id))
    db.add_all(
        [
            DoctorAvailability(
                doctor_id=doctor.id,
                day_of_week=slot.day_of_week,
                start_time=slot.start_time,
                end_time=slot.end_time,
                is_available=slot.is_available,
            )
            for slot in payload.slots
        ]
    )
    db.commit()
    return list(
        db.scalars(
            select(DoctorAvailability)
            .where(DoctorAvailability.doctor_id == doctor.id)
            .order_by(DoctorAvailability.day_of_week, DoctorAvailability.start_time)
        ).all()
    )


@router.get("/specialty/{specialty}", response_model=list[DoctorResponse])
def doctors_by_specialty(specialty: str, db: Session = Depends(get_db)) -> list[Doctor]:
    return list(
        db.scalars(
            _doctor_query()
            .join(Doctor.user)
            .where(
                func.lower(Doctor.specialty) == specialty.strip().lower(),
                Doctor.is_available.is_(True),
                User.is_active.is_(True),
            )
        ).unique().all()
    )


@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)) -> Doctor:
    doctor = db.scalar(_doctor_query().where(Doctor.id == doctor_id))
    if doctor is None or not doctor.user.is_active:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor
