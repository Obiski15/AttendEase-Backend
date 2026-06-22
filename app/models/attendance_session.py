import uuid

from sqlalchemy import Column, String, Date, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_assignment_id = Column(UUID(as_uuid=True), ForeignKey("course_assignments.id"), nullable=False)
    session_date = Column(Date, nullable=False)
    start_time = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    session_code = Column(String, unique=True, nullable=False)
    status = Column(String, default="ACTIVE")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    course_assignment = relationship("CourseAssignment", back_populates="attendance_sessions")
    attendance_records = relationship("AttendanceRecord", back_populates="attendance_session")
