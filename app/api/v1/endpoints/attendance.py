from datetime import datetime
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.models.attendance_record import AttendanceRecord
from app.models.user import User

router = APIRouter()


@router.post(
    "/check-in",
    response_model=schemas.AttendanceRecord,
    status_code=status.HTTP_201_CREATED,
    summary="Check in to an attendance session (student)",
)
def check_in(
    *,
    db: Session = Depends(deps.get_db),
    payload: schemas.AttendanceCheckIn,
    current_user: User = Depends(deps.require_student),
) -> Any:
    """Mark attendance by submitting the session code shown by the lecturer.

    Fails if the code is invalid, the window has closed/expired, or the
    student has already checked in to that session.
    """
    student = crud.student.get(db, current_user.id)
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")

    session = crud.attendance_session.get_by_code(db, session_code=payload.session_code)
    if not session:
        raise HTTPException(status_code=404, detail="Invalid session code.")
    if not crud.attendance_session.is_open(session):
        raise HTTPException(status_code=400, detail="This attendance session is closed or expired.")

    existing = crud.attendance_record.get_by_session_and_student(
        db, session_id=session.id, student_id=student.user_id
    )
    if existing:
        raise HTTPException(status_code=400, detail="You have already checked in to this session.")

    record = AttendanceRecord(
        session_id=session.id,
        student_id=student.user_id,
        check_in_time=datetime.utcnow(),
        status="PRESENT",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get(
    "/me",
    response_model=List[schemas.AttendanceRecord],
    summary="List my attendance records (student)",
)
def read_my_attendance(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.require_student),
) -> Any:
    """List the calling student's own attendance records."""
    return crud.attendance_record.get_multi_by_student(
        db, student_id=current_user.id, skip=skip, limit=limit
    )
