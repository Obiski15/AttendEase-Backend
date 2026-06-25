import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.academic_session import AcademicSession
    from app.models.attendance_session import AttendanceSession
    from app.models.course import Course
    from app.models.lecturer import Lecturer


class CourseAssignment(Base):
    __tablename__ = "course_assignments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id"))
    lecturer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lecturers.user_id"))
    academic_session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("academic_sessions.id")
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    course: Mapped["Course"] = relationship(back_populates="course_assignments")
    lecturer: Mapped["Lecturer"] = relationship(back_populates="course_assignments")
    academic_session: Mapped["AcademicSession"] = relationship(
        back_populates="course_assignments"
    )
    attendance_sessions: Mapped[List["AttendanceSession"]] = relationship(
        back_populates="course_assignment"
    )
