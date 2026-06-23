from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class DepartmentBase(BaseModel):
    name: Optional[str] = None


class DepartmentCreate(BaseModel):
    name: str


class DepartmentUpdate(DepartmentBase):
    pass


class Department(DepartmentBase):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
