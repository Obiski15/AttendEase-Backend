from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AttendanceRecordBase(BaseModel):
    session_id: Optional[UUID] = None
    student_id: Optional[UUID] = None
    check_in_time: Optional[datetime] = None
    status: Optional[str] = "PRESENT"


class AttendanceRecordCreate(AttendanceRecordBase):
    session_id: UUID
    student_id: UUID
    check_in_time: datetime


class AttendanceRecordUpdate(BaseModel):
    status: Optional[str] = None


class AttendanceRecord(AttendanceRecordBase):
    id: UUID
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
