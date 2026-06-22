import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint("session_id", "student_id", name="uq_session_student"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("attendance_sessions.id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.user_id"), nullable=False)
    check_in_time = Column(DateTime, nullable=False)
    status = Column(String, default="PRESENT")
    created_at = Column(DateTime, server_default=func.now())

    attendance_session = relationship("AttendanceSession", back_populates="attendance_records")
    student = relationship("Student", back_populates="attendance_records")
