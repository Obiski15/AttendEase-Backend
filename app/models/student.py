import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.attendance_record import AttendanceRecord
    from app.models.department import Department
    from app.models.user import User


class Student(Base):
    __tablename__ = "students"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    student_id: Mapped[str] = mapped_column(String, unique=True)
    matric_number: Mapped[str] = mapped_column(String, unique=True)
    department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id"))
    level: Mapped[str] = mapped_column(String)
    created_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="student_profile")
    department: Mapped["Department"] = relationship(back_populates="students")
    attendance_records: Mapped[List["AttendanceRecord"]] = relationship(back_populates="student")
