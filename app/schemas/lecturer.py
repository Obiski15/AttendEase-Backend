from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.schemas.user import User


class LecturerBase(BaseModel):
    staff_id: Optional[str] = None
    department_id: Optional[UUID] = None


class LecturerCreate(BaseModel):
    """Admin creates a lecturer: provisions the User account + Lecturer profile."""

    email: EmailStr
    password: str
    full_name: str
    staff_id: str
    department_id: UUID


class LecturerUpdate(LecturerBase):
    pass


class Lecturer(LecturerBase):
    user_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    user: Optional[User] = None

    model_config = {"from_attributes": True}
