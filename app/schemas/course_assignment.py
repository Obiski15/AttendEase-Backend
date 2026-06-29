from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import ConfigDict, BaseModel, Field

from app.schemas.course import Course
from app.schemas.lecturer import Lecturer
from app.schemas.academic_session import AcademicSession

class CourseAssignmentBase(BaseModel):
    course_id: Optional[UUID] = Field(default=None, description="ID of the course.", example="123e4567-e89b-12d3-a456-426614174006")
    lecturer_id: Optional[UUID] = Field(default=None, description="ID of the assigned lecturer.", example="123e4567-e89b-12d3-a456-426614174008")
    academic_session_id: Optional[UUID] = Field(default=None, description="ID of the academic session.", example="123e4567-e89b-12d3-a456-426614174007")


class CourseAssignmentCreate(BaseModel):
    course_id: UUID = Field(..., description="ID of the course.", example="123e4567-e89b-12d3-a456-426614174006")
    lecturer_id: UUID = Field(..., description="ID of the assigned lecturer.", example="123e4567-e89b-12d3-a456-426614174008")
    academic_session_id: UUID = Field(..., description="ID of the academic session.", example="123e4567-e89b-12d3-a456-426614174007")


class CourseAssignmentUpdate(CourseAssignmentBase):
    pass


class CourseAssignment(CourseAssignmentBase):
    id: UUID = Field(..., description="Unique ID of the course assignment.", example="123e4567-e89b-12d3-a456-426614174011")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp.")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp.")
    
    course: Optional[Course] = None
    lecturer: Optional[Lecturer] = None
    academic_session: Optional[AcademicSession] = None

    model_config = ConfigDict(from_attributes=True)
