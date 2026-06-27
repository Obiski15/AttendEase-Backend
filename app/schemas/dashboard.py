from datetime import date, datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class TrendPoint(BaseModel):
    date_str: str = Field(..., description="Date string for the trend point.", example="2026-06-25")
    count: int = Field(..., description="Count for this date.", example=150)

class PiePoint(BaseModel):
    label: str = Field(..., description="Label for the pie slice.", example="CSC301")
    count: int = Field(..., description="Count for this category.", example=42)

# ---- Admin ----
class AdminDashboard(BaseModel):
    total_students: int = Field(..., description="Total number of registered students in the system.", example=1542)
    total_lecturers: int = Field(..., description="Total number of registered lecturers in the system.", example=45)
    total_courses: int = Field(..., description="Total number of available courses.", example=120)
    active_sessions: int = Field(..., description="Number of currently active attendance sessions.", example=3)
    weekly_attendance_trend: List[TrendPoint] = Field(default_factory=list, description="System-wide check-ins over the last 7 days.")


# ---- Lecturer ----
class LecturerActiveSession(BaseModel):
    id: UUID = Field(..., description="Unique ID of the attendance session.", example="123e4567-e89b-12d3-a456-426614174000")
    course_code: str = Field(..., description="Course code.", example="CSC301")
    course_title: str = Field(..., description="Course title.", example="Introduction to Artificial Intelligence")
    session_code: str = Field(..., description="The unique code students use to check in.", example="XYZ12345")
    expires_at: datetime = Field(..., description="When the attendance session will automatically close.", example="2026-06-27T10:30:00Z")
    geofencing_enabled: bool = Field(..., description="Whether location spoofing prevention is active.", example=True)
    radius_meters: int | None = Field(default=None, description="The geofence radius in meters, if enabled.", example=50)


class LecturerCourse(BaseModel):
    course_assignment_id: UUID = Field(..., description="Unique ID of the course assignment.", example="123e4567-e89b-12d3-a456-426614174001")
    course_code: str = Field(..., description="Course code.", example="CSC301")
    course_title: str = Field(..., description="Course title.", example="Introduction to Artificial Intelligence")
    credit_units: int = Field(..., description="Number of credit units.", example=3)


class LecturerDashboard(BaseModel):
    full_name: str = Field(..., description="Full name of the lecturer.", example="Dr. John Doe")
    assigned_courses: int = Field(..., description="Number of courses assigned to this lecturer.", example=4)
    total_sessions: int = Field(..., description="Total number of attendance sessions opened by this lecturer.", example=12)
    active_sessions: List[LecturerActiveSession] = Field(..., description="List of currently open attendance sessions.")
    courses: List[LecturerCourse] = Field(..., description="List of assigned courses.")
    course_distribution: List[PiePoint] = Field(default_factory=list, description="Distribution of attendance sessions per course.")


# ---- Student ----
class RecentAttendance(BaseModel):
    course_code: str = Field(..., description="Code of the course.", example="CSC301")
    course_title: str = Field(..., description="Title of the course.", example="Introduction to Artificial Intelligence")
    session_date: date = Field(..., description="Date of the attendance session.", example="2026-06-25")
    check_in_time: datetime = Field(..., description="Exact time the student checked in.", example="2026-06-25T10:15:30Z")
    status: str = Field(..., description="Status of the student's attendance.", example="PRESENT")


class StudentDashboard(BaseModel):
    full_name: str = Field(..., description="Full name of the student.", example="Jane Smith")
    attendance_percentage: float = Field(..., description="Overall attendance percentage across all enrolled courses.", example=92.5)
    present_count: int = Field(..., description="Total number of sessions attended.", example=37)
    total_count: int = Field(..., description="Total number of sessions conducted for enrolled courses.", example=40)
    recent_attendance: List[RecentAttendance] = Field(..., description="History of recent attendance records.")

