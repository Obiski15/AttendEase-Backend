from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CourseBase(BaseModel):
    course_code: Optional[str] = None
    title: Optional[str] = None
    credit_units: Optional[int] = None
    department_id: Optional[UUID] = None


class CourseCreate(BaseModel):
    course_code: str
    title: str
    credit_units: int
    department_id: UUID


class CourseUpdate(CourseBase):
    pass


class Course(CourseBase):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
