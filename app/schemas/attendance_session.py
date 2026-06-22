from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AttendanceSessionBase(BaseModel):
    course_assignment_id: Optional[UUID] = None
    session_date: Optional[date] = None
    start_time: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    session_code: Optional[str] = None
    status: Optional[str] = "ACTIVE"


class AttendanceSessionCreate(AttendanceSessionBase):
    course_assignment_id: UUID
    session_date: date
    start_time: datetime
    expires_at: datetime
    session_code: str


class AttendanceSessionUpdate(BaseModel):
    status: Optional[str] = None
    expires_at: Optional[datetime] = None


class AttendanceSession(AttendanceSessionBase):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
