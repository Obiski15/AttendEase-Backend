import logging
from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.models.attendance_session import AttendanceSession
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


def _assert_can_manage(db: Session, session: AttendanceSession, user: User) -> None:
    """Admins manage any session; lecturers only their own assignments."""
    if user.role == "ADMIN":
        return
    assignment = crud.course_assignment.get(db, id=session.course_assignment_id)
    if user.role == "LECTURER" and assignment and assignment.lecturer_id == user.id:
        return
    logger.warning(f"User {user.id} denied manage access for session {session.id}", extra={"user_id": user.id, "session_id": session.id, "action": "manage_session_denied"})
    raise HTTPException(
        status_code=403, detail="Not enough privileges for this session."
    )


@router.post(
    "/",
    response_model=schemas.AttendanceSession,
    status_code=status.HTTP_201_CREATED,
    summary="Open an attendance session (lecturer)",
)
def open_attendance_session(
    *,
    db: Session = Depends(deps.get_db),
    session_in: schemas.AttendanceSessionCreate,
    current_user: User = Depends(deps.require_staff),
) -> Any:
    """Open an attendance window for a course assignment and generate a code
    students use to check in. Lecturer (own assignment) or admin.
    """
    assignment = crud.course_assignment.get(db, id=session_in.course_assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Course assignment not found.")
    if current_user.role == "LECTURER" and assignment.lecturer_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="You are not assigned to this course."
        )

    academic_session = crud.academic_session.get(db, id=assignment.academic_session_id)
    if not academic_session:
        raise HTTPException(
            status_code=404, detail="Academic session linked to assignment not found."
        )
    if not academic_session.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot open attendance session. The academic session is not active.",
        )

    from datetime import date

    today = date.today()
    if academic_session.start_date and today < academic_session.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot open attendance session. The academic session has not started yet.",
        )
    if academic_session.end_date and today > academic_session.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot open attendance session. The academic session has already ended.",
        )

    opened_session = crud.attendance_session.open_session(db=db, obj_in=session_in)
    logger.info(f"Attendance session {opened_session.id} opened", extra={"session_id": opened_session.id, "course_assignment_id": session_in.course_assignment_id, "action": "open_attendance_session"})
    return opened_session


@router.get(
    "/",
    response_model=schemas.PaginatedResponse[schemas.AttendanceSession],
    summary="List attendance sessions (staff)",
)
def read_attendance_sessions(
    db: Session = Depends(deps.get_db),
    course_assignment_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.require_staff),
) -> Any:
    """List attendance sessions, optionally filtered by course assignment.

    Lecturers must pass a `course_assignment_id` they own.
    """
    if course_assignment_id:
        assignment = crud.course_assignment.get(db, id=course_assignment_id)
        if not assignment:
            raise HTTPException(status_code=404, detail="Course assignment not found.")
        if (
            current_user.role == "LECTURER"
            and assignment.lecturer_id != current_user.id
        ):
            raise HTTPException(status_code=403, detail="Not enough privileges.")
        items, total = crud.attendance_session.get_paginated_by_assignment(
            db, course_assignment_id=course_assignment_id, skip=skip, limit=limit
        )
        return {"items": items, "total": total, "skip": skip, "limit": limit}
    if current_user.role == "LECTURER":
        items, total = crud.attendance_session.get_paginated_by_lecturer(
            db, lecturer_id=current_user.id, skip=skip, limit=limit
        )
        return {"items": items, "total": total, "skip": skip, "limit": limit}
    items, total = crud.attendance_session.get_paginated(db, skip=skip, limit=limit)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get(
    "/{session_id}",
    response_model=schemas.AttendanceSession,
    summary="Get an attendance session (staff)",
)
def read_attendance_session(
    *,
    db: Session = Depends(deps.get_db),
    session_id: UUID,
    current_user: User = Depends(deps.require_staff),
) -> Any:
    session = crud.attendance_session.get(db=db, id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Attendance session not found")
    _assert_can_manage(db, session, current_user)
    return session


@router.post(
    "/{session_id}/close",
    response_model=schemas.AttendanceSession,
    status_code=200,
    summary="Close an active attendance session",
    description=(
        "Allows an authorized Lecturer to manually terminate a live attendance tracking session before its scheduled expiration time."
    ),
    responses={
        200: {
            "description": "Success - Attendance session has been successfully closed."
        },
        400: {
            "description": "Bad Request - Invalid geofence parameters or lecturer is not assigned to this course"
        },
        401: {
            "description": "Unauthorized - Missing or invalid Bearer JWT security token"
        },
        403: {
            "description": "Forbidden - Current user role is not authorized (Lecturer permissions required)"
        },
        404: {
            "description": "Not Found - The specified course or active academic session does not exist"
        }
    }
)
def close_attendance_session(
    *,
    db: Session = Depends(deps.get_db),
    session_id: UUID,
    current_user: User = Depends(deps.require_staff),
) -> Any:
    """Manually close an open attendance window. Lecturer (own) or admin."""
    session = crud.attendance_session.get(db=db, id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Attendance session not found")
    _assert_can_manage(db, session, current_user)
    closed_session = crud.attendance_session.close(db=db, db_obj=session)
    logger.info(f"Attendance session {session_id} closed manually", extra={"session_id": session_id, "action": "close_attendance_session_manual"})
    return closed_session


@router.get(
    "/{session_id}/records",
    response_model=List[schemas.AttendanceRecord],
    summary="List check-ins for a session (staff)",
)
def read_session_records(
    *,
    db: Session = Depends(deps.get_db),
    session_id: UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.require_staff),
) -> Any:
    """List all students who checked in to this session. Lecturer (own) or admin."""
    session = crud.attendance_session.get(db=db, id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Attendance session not found")
    _assert_can_manage(db, session, current_user)
    return crud.attendance_record.get_multi_by_session(
        db, session_id=session_id, skip=skip, limit=limit
    )
