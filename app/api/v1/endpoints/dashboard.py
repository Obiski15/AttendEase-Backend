import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.crud import crud_dashboard
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/admin",
    response_model=schemas.AdminDashboard,
    summary="Admin dashboard overview",
)
def admin_dashboard(
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_admin),
) -> Any:
    """System-wide totals: students, lecturers, courses and active sessions. Admin only."""
    return crud_dashboard.admin_stats(db)


@router.get(
    "/lecturer",
    response_model=schemas.LecturerDashboard,
    summary="Lecturer dashboard overview",
)
def lecturer_dashboard(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_lecturer),
) -> Any:
    """Assigned courses, active sessions and total sessions for the logged-in lecturer."""
    return crud_dashboard.lecturer_dashboard(
        db, lecturer_id=current_user.id, full_name=current_user.full_name
    )


@router.get(
    "/student",
    response_model=schemas.StudentDashboard,
    summary="Student dashboard overview",
)
def student_dashboard(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_student),
) -> Any:
    """Attendance percentage and recent check-ins for the logged-in student."""
    student = crud.student.get(db, current_user.id)
    if not student:
        logger.error(f"Student profile missing for user {current_user.id}", extra={"user_id": current_user.id, "action": "dashboard_student_missing"})
        raise HTTPException(status_code=404, detail="Student profile not found.")
    return crud_dashboard.student_dashboard(
        db, student_id=current_user.id, full_name=current_user.full_name
    )
