import uuid

from sqlalchemy import Column, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CourseAssignment(Base):
    __tablename__ = "course_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    lecturer_id = Column(UUID(as_uuid=True), ForeignKey("lecturers.user_id"), nullable=False)
    academic_session_id = Column(UUID(as_uuid=True), ForeignKey("academic_sessions.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    course = relationship("Course", back_populates="course_assignments")
    lecturer = relationship("Lecturer", back_populates="course_assignments")
    academic_session = relationship("AcademicSession", back_populates="course_assignments")
    attendance_sessions = relationship("AttendanceSession", back_populates="course_assignment")
