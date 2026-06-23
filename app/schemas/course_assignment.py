from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CourseAssignmentBase(BaseModel):
    course_id: Optional[UUID] = None
    lecturer_id: Optional[UUID] = None
    academic_session_id: Optional[UUID] = None


class CourseAssignmentCreate(BaseModel):
    course_id: UUID
    lecturer_id: UUID
    academic_session_id: UUID


class CourseAssignmentUpdate(CourseAssignmentBase):
    pass


class CourseAssignment(CourseAssignmentBase):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
