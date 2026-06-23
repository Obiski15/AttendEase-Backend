from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.schemas.user import User


class StudentBase(BaseModel):
    student_id: Optional[str] = None
    matric_number: Optional[str] = None
    department_id: Optional[UUID] = None
    level: Optional[str] = None


class StudentCreate(StudentBase):
    """Admin creates a student: provisions the User account + Student profile."""

    email: EmailStr
    password: str
    full_name: str
    student_id: str
    matric_number: str
    department_id: UUID
    level: str


class StudentRegister(BaseModel):
    """Public self-registration payload for a new student."""

    email: EmailStr
    password: str
    full_name: str
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
    user: Optional[User] = None

    model_config = {"from_attributes": True}
