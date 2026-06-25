from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.base import Base
from app.db.session import engine
from app.middleware.logging_middleware import LoggingMiddleware

# Initialize structured logging
setup_logging()

# This automatically creates tables if they don't exist

Base.metadata.create_all(bind=engine)

description = "Backend API for the AttendEase attendance management system"

tags_metadata = [
    {
        "name": "auth",
        "description": "Login, token refresh, registration, and current user.",
    },
    {"name": "users", "description": "User account administration (admin)."},
    {"name": "departments", "description": "Academic departments."},
    {"name": "students", "description": "Student accounts and profiles."},
    {"name": "lecturers", "description": "Lecturer accounts and profiles."},
    {"name": "courses", "description": "Courses offered by departments."},
    {"name": "academic-sessions", "description": "Academic sessions / semesters."},
    {
        "name": "course-assignments",
        "description": "Assigning lecturers to courses per session.",
    },
    {
        "name": "attendance-sessions",
        "description": "Attendance windows opened by lecturers.",
    },
    {
        "name": "attendance",
        "description": "Student check-in and personal attendance records.",
    },
    {
        "name": "dashboard",
        "description": "Role-specific dashboard summaries for admin, lecturer and student.",
    },
]

app = FastAPI(
    title="AttendEase API",
    description=description,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata,
)

app.add_middleware(LoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["health"], summary="Health check")
def read_root():
    return {"message": "Welcome to AttendEase API"}
