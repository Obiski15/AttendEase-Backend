from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AttendanceSessionBase(BaseModel):
    course_assignment_id: Optional[UUID] = Field(default=None, description="ID of the course assignment.", example="123e4567-e89b-12d3-a456-426614174011")
    session_date: Optional[date] = Field(default=None, description="Date of the session.", example="2026-06-25")
    start_time: Optional[datetime] = Field(default=None, description="Session start time.", example="2026-06-25T10:00:00Z")
    expires_at: Optional[datetime] = Field(default=None, description="When the session closes.", example="2026-06-25T11:00:00Z")
    session_code: Optional[str] = Field(default=None, description="Check-in code.", example="XYZ12345")
    status: Optional[str] = Field(default="ACTIVE", description="Session status.", example="ACTIVE")
    geofencing_enabled: Optional[bool] = Field(default=False, description="Is geofencing enforced?", example=True)
    latitude: Optional[float] = Field(default=None, description="Center latitude.", example=37.7749)
    longitude: Optional[float] = Field(default=None, description="Center longitude.", example=-122.4194)
    radius_meters: Optional[int] = Field(default=50, description="Geofence radius.", example=50)


class AttendanceSessionCreate(BaseModel):
    """Open a new attendance window for a course assignment."""

    id: Optional[UUID] = Field(default=None, description="Optional client-generated UUID for offline sync.", example="123e4567-e89b-12d3-a456-426614174011")
    course_assignment_id: UUID = Field(..., description="ID of the course assignment.", example="123e4567-e89b-12d3-a456-426614174011")
    session_date: Optional[date] = Field(default=None, description="Defaults to today.", example="2026-06-25")
    start_time: Optional[datetime] = Field(default=None, description="Session start time.", example="2026-06-25T10:00:00Z")
    expires_at: Optional[datetime] = Field(default=None, description="When the session closes.", example="2026-06-25T11:00:00Z")
    duration_minutes: Optional[int] = Field(
        default=60, ge=1, description="Used when expires_at is not given.", example=60
    )
    session_code: Optional[str] = Field(
        default=None, description="Auto-generated if omitted.", example="XYZ12345"
    )
    geofencing_enabled: Optional[bool] = Field(
        default=False, description="Enable geofencing for this session.", example=True
    )
    latitude: Optional[float] = Field(
        default=None, description="Center latitude of the geofence.", example=37.7749
    )
    longitude: Optional[float] = Field(
        default=None, description="Center longitude of the geofence.", example=-122.4194
    )
    radius_meters: Optional[int] = Field(
        default=50, ge=5, description="Allowed radius in meters.", example=50
    )


class AttendanceSessionUpdate(BaseModel):
    status: Optional[str] = Field(default=None, description="Update status.", example="CLOSED")
    expires_at: Optional[datetime] = Field(default=None, description="Extend or shorten the expiry.", example="2026-06-25T11:30:00Z")


class AttendanceSession(AttendanceSessionBase):
    id: UUID = Field(..., description="Unique ID of the attendance session.", example="123e4567-e89b-12d3-a456-426614174012")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp.")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp.")
    records_count: int = Field(default=0, description="Number of students who have checked in.", example=45)
    total_students: int = Field(default=0, description="Total number of students enrolled.", example=50)

    model_config = ConfigDict(from_attributes=True)
