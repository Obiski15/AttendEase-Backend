from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class LecturerBase(BaseModel):
    staff_id: Optional[str] = None
    department_id: Optional[UUID] = None


class LecturerCreate(LecturerBase):
    user_id: UUID
    staff_id: str
    department_id: UUID


class LecturerUpdate(LecturerBase):
    pass


class Lecturer(LecturerBase):
    user_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
