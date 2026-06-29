import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.course_assignment import CourseAssignment
    from app.models.department import Department
    from app.models.user import User


class Lecturer(Base):
    __tablename__ = "lecturers"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    staff_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id"))
    created_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="lecturer_profile")
    department: Mapped["Department"] = relationship(back_populates="lecturers")
    course_assignments: Mapped[List["CourseAssignment"]] = relationship(
        back_populates="lecturer"
    )
