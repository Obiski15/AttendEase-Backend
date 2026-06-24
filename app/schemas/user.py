from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = "ACTIVE"
    profile_image_url: Optional[str] = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str
    status: Optional[str] = "ACTIVE"
    profile_image_url: Optional[str] = None


class UserUpdate(UserBase):
    password: Optional[str] = None


class User(UserBase):
    id: UUID
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str


class ProfileUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    profile_image_url: Optional[str] = None
