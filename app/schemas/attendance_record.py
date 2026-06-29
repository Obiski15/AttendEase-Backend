from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AttendanceRecordBase(BaseModel):
    session_id: Optional[UUID] = Field(default=None, description="ID of the attendance session.", example="123e4567-e89b-12d3-a456-426614174000")
    student_id: Optional[UUID] = Field(default=None, description="ID of the student.", example="123e4567-e89b-12d3-a456-426614174001")
    check_in_time: Optional[datetime] = Field(default=None, description="Time the student checked in.", example="2026-06-25T10:15:30Z")
    latitude: Optional[float] = Field(default=None, description="Student's latitude at check-in time.", example=37.7749)
    longitude: Optional[float] = Field(default=None, description="Student's longitude at check-in time.", example=-122.4194)
    status: Optional[str] = Field(default="PRESENT", description="Attendance status (PRESENT, ABSENT, etc.)", example="PRESENT")


class AttendanceRecordCreate(BaseModel):
    session_id: UUID = Field(..., description="ID of the attendance session.", example="123e4567-e89b-12d3-a456-426614174000")
    student_id: UUID = Field(..., description="ID of the student.", example="123e4567-e89b-12d3-a456-426614174001")
    check_in_time: datetime = Field(..., description="Time the student checked in.", example="2026-06-25T10:15:30Z")


class AttendanceCheckIn(BaseModel):
    """Student check-in: submit the code shown by the lecturer."""

    session_code: str = Field(
        ..., description="The code for the open attendance session.", example="XYZ12345"
    )
    latitude: Optional[float] = Field(
        default=None, description="Current latitude of the student.", example=37.7749
    )
    longitude: Optional[float] = Field(
        default=None, description="Current longitude of the student.", example=-122.4194
    )
    check_in_time: Optional[datetime] = Field(
        default=None, description="Optional offline check-in time.", example="2026-06-25T10:15:30Z"
    )


class AttendanceRecordUpdate(BaseModel):
    status: Optional[str] = Field(default=None, description="Updated attendance status.", example="ABSENT")


class AttendanceRecord(AttendanceRecordBase):
    id: UUID = Field(..., description="Unique ID of the attendance record.", example="123e4567-e89b-12d3-a456-426614174002")
    created_at: Optional[datetime] = Field(default=None, description="When the record was created.")

    model_config = ConfigDict(from_attributes=True)


class AttendanceHistoryRecord(AttendanceRecord):
    course_code: Optional[str] = Field(default=None, description="Code of the course.", example="CSC301")
    course_title: Optional[str] = Field(default=None, description="Title of the course.", example="Data Structures")
