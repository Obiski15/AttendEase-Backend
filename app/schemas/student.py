from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class StudentBase(BaseModel):
    student_id: Optional[str] = None
    matric_number: Optional[str] = None
    department_id: Optional[UUID] = None
    level: Optional[str] = None


class StudentCreate(StudentBase):
    user_id: UUID
    student_id: str
    matric_number: str
    department_id: UUID
    level: str


class StudentUpdate(StudentBase):
    pass


class Student(StudentBase):
    user_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
