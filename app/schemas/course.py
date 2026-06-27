from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CourseBase(BaseModel):
    course_code: Optional[str] = Field(default=None, description="Course code (e.g., CSC301).", example="CSC301")
    title: Optional[str] = Field(default=None, description="Full title of the course.", example="Data Structures")
    credit_units: Optional[int] = Field(default=None, description="Number of credit units.", example=3)
    department_id: Optional[UUID] = Field(default=None, description="ID of the department offering the course.", example="123e4567-e89b-12d3-a456-426614174005")


class CourseCreate(BaseModel):
    course_code: str = Field(..., description="Course code (e.g., CSC301).", example="CSC301")
    title: str = Field(..., description="Full title of the course.", example="Data Structures")
    credit_units: int = Field(..., description="Number of credit units.", example=3)
    department_id: UUID = Field(..., description="ID of the department offering the course.", example="123e4567-e89b-12d3-a456-426614174005")


class CourseUpdate(CourseBase):
    pass


class Course(CourseBase):
    id: UUID = Field(..., description="Unique ID of the course.", example="123e4567-e89b-12d3-a456-426614174006")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp.")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp.")

    model_config = {"from_attributes": True}
