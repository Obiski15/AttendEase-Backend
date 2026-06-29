from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import ConfigDict, BaseModel, EmailStr, Field

from app.schemas.user import User


class StudentBase(BaseModel):
    student_id: Optional[str] = Field(default=None, description="University-assigned student ID.", example="STU-001234")
    matric_number: Optional[str] = Field(default=None, description="Matriculation number.", example="M1234567")
    department_id: Optional[UUID] = Field(default=None, description="ID of the student's department.", example="123e4567-e89b-12d3-a456-426614174005")
    level: Optional[str] = Field(default=None, description="Academic level (e.g., 100, 200, 300).", example="200")


class StudentCreate(BaseModel):
    """Admin creates a student: provisions the User account + Student profile."""

    email: EmailStr = Field(..., description="Student's email address.", example="student@university.edu")
    password: str = Field(..., description="Initial password.", example="SecurePass123!")
    full_name: str = Field(..., description="Student's full name.", example="Jane Smith")
    student_id: str = Field(..., description="University-assigned student ID.", example="STU-001234")
    matric_number: str = Field(..., description="Matriculation number.", example="M1234567")
    department_id: UUID = Field(..., description="ID of the student's department.", example="123e4567-e89b-12d3-a456-426614174005")
    level: str = Field(..., description="Academic level.", example="200")


class StudentRegister(BaseModel):
    """Public self-registration payload for a new student."""

    email: EmailStr = Field(..., description="Student's email address.", example="student@university.edu")
    password: str = Field(..., description="Initial password.", example="SecurePass123!")
    full_name: str = Field(..., description="Student's full name.", example="Jane Smith")
    student_id: str = Field(..., description="University-assigned student ID.", example="STU-001234")
    matric_number: str = Field(..., description="Matriculation number.", example="M1234567")
    department_id: UUID = Field(..., description="ID of the student's department.", example="123e4567-e89b-12d3-a456-426614174005")
    level: str = Field(..., description="Academic level.", example="200")


class StudentUpdate(StudentBase):
    pass


class Student(StudentBase):
    user_id: UUID = Field(..., description="Foreign key to the User record.")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp.")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp.")
    
    user: Optional[User] = Field(default=None, description="The user details associated with this student.")
    department: Optional[Department] = Field(default=None, description="The department the student belongs to.")

    model_config = ConfigDict(from_attributes=True)
