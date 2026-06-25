from fastapi import APIRouter

from app.api.v1.endpoints import (
    academic_sessions,
    attendance,
    attendance_sessions,
    auth,
    course_assignments,
    courses,
    dashboard,
    departments,
    lecturers,
    students,
    users,
    websockets,
)

api_router = APIRouter()

api_router.include_router(websockets.router, prefix="/ws", tags=["websockets"])

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    departments.router, prefix="/departments", tags=["departments"]
)
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(lecturers.router, prefix="/lecturers", tags=["lecturers"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(
    academic_sessions.router, prefix="/academic-sessions", tags=["academic-sessions"]
)
api_router.include_router(
    course_assignments.router, prefix="/course-assignments", tags=["course-assignments"]
)
api_router.include_router(
    attendance_sessions.router,
    prefix="/attendance-sessions",
    tags=["attendance-sessions"],
)
api_router.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
