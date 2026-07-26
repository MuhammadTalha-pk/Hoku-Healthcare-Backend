from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Symptom(Base):
    __tablename__ = "symptoms"

    id: Mapped[int] = mapped_column(primary_key=True)
    symptom_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    possible_conditions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    severity_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    specialist_recommended: Mapped[str | None] = mapped_column(String(255), nullable=True)
