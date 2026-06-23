import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.attendance_session import AttendanceSession
    from app.models.student import Student


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint("session_id", "student_id", name="uq_session_student"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("attendance_sessions.id"))
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.user_id"))
    check_in_time: Mapped[datetime] = mapped_column()
    status: Mapped[str] = mapped_column(String, default="PRESENT")
    created_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now())

    attendance_session: Mapped["AttendanceSession"] = relationship(back_populates="attendance_records")
    student: Mapped["Student"] = relationship(back_populates="attendance_records")
