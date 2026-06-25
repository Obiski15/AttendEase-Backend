import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.course_assignment import CourseAssignment
    from app.models.department import Department


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    course_code: Mapped[str] = mapped_column(String, unique=True)
    title: Mapped[str] = mapped_column(String)
    credit_units: Mapped[int] = mapped_column(Integer)
    department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id"))
    created_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    department: Mapped["Department"] = relationship(back_populates="courses")
    course_assignments: Mapped[List["CourseAssignment"]] = relationship(
        back_populates="course"
    )
