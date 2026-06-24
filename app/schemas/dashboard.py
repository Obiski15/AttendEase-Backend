from datetime import date, datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel


# ---- Admin ----
class AdminDashboard(BaseModel):
    total_students: int
    total_lecturers: int
    total_courses: int
    active_sessions: int


# ---- Lecturer ----
class LecturerActiveSession(BaseModel):
    id: UUID
    course_code: str
    course_title: str
    session_code: str
    expires_at: datetime


class LecturerCourse(BaseModel):
    course_assignment_id: UUID
    course_code: str
    course_title: str
    credit_units: int


class LecturerDashboard(BaseModel):
    full_name: str
    assigned_courses: int
    total_sessions: int
    active_sessions: List[LecturerActiveSession]
    courses: List[LecturerCourse]


# ---- Student ----
class RecentAttendance(BaseModel):
    course_code: str
    course_title: str
    session_date: date
    check_in_time: datetime
    status: str


class StudentDashboard(BaseModel):
    full_name: str
    attendance_percentage: float
    present_count: int
    total_count: int
    recent_attendance: List[RecentAttendance]
