from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AttendanceSessionBase(BaseModel):
    course_assignment_id: Optional[UUID] = None
    session_date: Optional[date] = None
    start_time: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    session_code: Optional[str] = None
    status: Optional[str] = "ACTIVE"


class AttendanceSessionCreate(BaseModel):
    """Open a new attendance window for a course assignment.

    `session_code` is auto-generated and `start_time` defaults to now if
    omitted. Provide either `expires_at` or `duration_minutes` to set when the
    window closes (defaults to 60 minutes).
    """

    course_assignment_id: UUID
    session_date: Optional[date] = Field(default=None, description="Defaults to today.")
    start_time: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(default=60, ge=1, description="Used when expires_at is not given.")
    session_code: Optional[str] = Field(default=None, description="Auto-generated if omitted.")


class AttendanceSessionUpdate(BaseModel):
    status: Optional[str] = None
    expires_at: Optional[datetime] = None


class AttendanceSession(AttendanceSessionBase):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
