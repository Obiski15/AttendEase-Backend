from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import ConfigDict, BaseModel, Field


class DepartmentBase(BaseModel):
    name: Optional[str] = Field(default=None, description="Name of the department.", example="Computer Science")


class DepartmentCreate(BaseModel):
    name: str = Field(..., description="Name of the department.", example="Computer Science")


class DepartmentUpdate(DepartmentBase):
    pass


class Department(DepartmentBase):
    id: UUID = Field(..., description="Unique ID of the department.", example="123e4567-e89b-12d3-a456-426614174005")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp.")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp.")

    model_config = ConfigDict(from_attributes=True)
