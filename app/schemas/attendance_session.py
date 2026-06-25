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
    geofencing_enabled: Optional[bool] = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_meters: Optional[int] = 50


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
    duration_minutes: Optional[int] = Field(
        default=60, ge=1, description="Used when expires_at is not given."
    )
    session_code: Optional[str] = Field(
        default=None, description="Auto-generated if omitted."
    )
    geofencing_enabled: Optional[bool] = Field(
        default=False, description="Enable geofencing for this session."
    )
    latitude: Optional[float] = Field(
        default=None, description="Center latitude of the geofence."
    )
    longitude: Optional[float] = Field(
        default=None, description="Center longitude of the geofence."
    )
    radius_meters: Optional[int] = Field(
        default=50, ge=5, description="Allowed radius in meters."
    )


class AttendanceSessionUpdate(BaseModel):
    status: Optional[str] = None
    expires_at: Optional[datetime] = None


class AttendanceSession(AttendanceSessionBase):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    records_count: int = 0
    total_students: int = 0

    model_config = {"from_attributes": True}
