import uuid
from datetime import datetime, date
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, String, Date, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.course_assignment import CourseAssignment


class AcademicSession(Base):
    __tablename__ = "academic_sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_name: Mapped[str] = mapped_column(String)
    semester: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    course_assignments: Mapped[List["CourseAssignment"]] = relationship(
        back_populates="academic_session"
    )
