import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Date, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.attendance_record import AttendanceRecord
    from app.models.course_assignment import CourseAssignment


class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    course_assignment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("course_assignments.id"))
    session_date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[datetime] = mapped_column()
    expires_at: Mapped[datetime] = mapped_column()
    session_code: Mapped[str] = mapped_column(String, unique=True)
    status: Mapped[str] = mapped_column(String, default="ACTIVE")
    created_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now(), onupdate=func.now())

    course_assignment: Mapped["CourseAssignment"] = relationship(back_populates="attendance_sessions")
    attendance_records: Mapped[List["AttendanceRecord"]] = relationship(back_populates="attendance_session")
