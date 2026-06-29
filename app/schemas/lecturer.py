from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import User
from app.schemas.department import Department

class LecturerBase(BaseModel):
    staff_id: Optional[str] = Field(default=None, description="University-assigned staff ID.", example="STAFF-00123")
    department_id: Optional[UUID] = Field(default=None, description="ID of the lecturer's department.", example="123e4567-e89b-12d3-a456-426614174005")


class LecturerCreate(BaseModel):
    """Admin creates a lecturer: provisions the User account + Lecturer profile."""

    email: EmailStr = Field(..., description="Lecturer's email address.", example="lecturer@university.edu")
    password: str = Field(..., description="Initial password.", example="SecurePass123!")
    full_name: str = Field(..., description="Lecturer's full name.", example="Dr. Jane Smith")
    staff_id: str = Field(..., description="University-assigned staff ID.", example="STAFF-00123")
    department_id: UUID = Field(..., description="ID of the lecturer's department.", example="123e4567-e89b-12d3-a456-426614174005")


class LecturerUpdate(LecturerBase):
    pass


class Lecturer(LecturerBase):
    user_id: UUID = Field(..., description="ID of the associated User account.", example="123e4567-e89b-12d3-a456-426614174099")
    created_at: Optional[datetime] = Field(default=None, description="Profile creation timestamp.")
    updated_at: Optional[datetime] = Field(default=None, description="Profile last update timestamp.")
    user: Optional[User] = Field(default=None, description="The nested User account details.")
    department: Optional[Department] = Field(default=None, description="The department the lecturer belongs to.")

    model_config = ConfigDict(from_attributes=True)
