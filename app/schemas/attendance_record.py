from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AttendanceRecordBase(BaseModel):
    session_id: Optional[UUID] = None
    student_id: Optional[UUID] = None
    check_in_time: Optional[datetime] = None
    status: Optional[str] = "PRESENT"


class AttendanceRecordCreate(BaseModel):
    session_id: UUID
    student_id: UUID
    check_in_time: datetime


class AttendanceCheckIn(BaseModel):
    """Student check-in: submit the code shown by the lecturer."""

    session_code: str = Field(..., description="The code for the open attendance session.")


class AttendanceRecordUpdate(BaseModel):
    status: Optional[str] = None


class AttendanceRecord(AttendanceRecordBase):
    id: UUID
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
