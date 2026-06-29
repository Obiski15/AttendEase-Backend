from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: Optional[EmailStr] = Field(default=None, description="User's email address.", example="user@university.edu")
    full_name: Optional[str] = Field(default=None, description="User's full name.", example="Jane Doe")
    role: Optional[str] = Field(default=None, description="Role of the user (Admin, Lecturer, Student).", example="Student")
    status: Optional[str] = Field(default="ACTIVE", description="Account status.", example="ACTIVE")
    profile_image_url: Optional[str] = Field(default=None, description="URL to the user's profile picture.")


class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="User's email address.", example="user@university.edu")
    password: str = Field(..., description="Plain text password (will be hashed).", example="StrongPassword123!")
    full_name: str = Field(..., description="User's full name.", example="Jane Doe")
    role: str = Field(..., description="Role of the user (Admin, Lecturer, Student).", example="Student")
    status: Optional[str] = Field(default="ACTIVE", description="Account status.", example="ACTIVE")
    profile_image_url: Optional[str] = Field(default=None, description="URL to the user's profile picture.")


class UserUpdate(UserBase):
    password: Optional[str] = Field(default=None, description="New password (will be hashed).")


class User(UserBase):
    id: UUID = Field(..., description="Unique ID of the user.", example="123e4567-e89b-12d3-a456-426614174099")
    last_login: Optional[datetime] = Field(default=None, description="Timestamp of the user's last login.")
    created_at: Optional[datetime] = Field(default=None, description="Timestamp of account creation.")
    updated_at: Optional[datetime] = Field(default=None, description="Timestamp of last account update.")

    model_config = ConfigDict(from_attributes=True)


class PasswordUpdate(BaseModel):
    old_password: str = Field(..., description="Current password for verification.", example="OldPassword123!")
    new_password: str = Field(..., description="New desired password.", example="NewPassword456!")


class ProfileUpdate(BaseModel):
    email: Optional[EmailStr] = Field(default=None, description="New email address.", example="new_email@university.edu")
    full_name: Optional[str] = Field(default=None, description="New full name.", example="Jane A. Doe")
    profile_image_url: Optional[str] = Field(default=None, description="New profile picture URL.")
