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
    course_assignment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("course_assignments.id", ondelete="CASCADE")
    )
    session_date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[datetime] = mapped_column()
    expires_at: Mapped[datetime] = mapped_column()
    session_code: Mapped[str] = mapped_column(String, unique=True)
    status: Mapped[str] = mapped_column(String, default="ACTIVE")
    geofencing_enabled: Mapped[bool] = mapped_column(default=False)
    latitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    radius_meters: Mapped[Optional[int]] = mapped_column(default=50, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    course_assignment: Mapped["CourseAssignment"] = relationship(
        back_populates="attendance_sessions"
    )
    attendance_records: Mapped[List["AttendanceRecord"]] = relationship(
        back_populates="attendance_session",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    @property
    def records_count(self) -> int:
        return len(self.attendance_records)

    @property
    def total_students(self) -> int:
        if (
            self.course_assignment
            and self.course_assignment.course
            and self.course_assignment.course.department
        ):
            return len(self.course_assignment.course.department.students)
        return 0
