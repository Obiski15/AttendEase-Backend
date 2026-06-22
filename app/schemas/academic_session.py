from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AcademicSessionBase(BaseModel):
    session_name: Optional[str] = None
    semester: Optional[str] = None
    is_active: Optional[bool] = False


class AcademicSessionCreate(AcademicSessionBase):
    session_name: str
    semester: str


class AcademicSessionUpdate(AcademicSessionBase):
    pass


class AcademicSession(AcademicSessionBase):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
