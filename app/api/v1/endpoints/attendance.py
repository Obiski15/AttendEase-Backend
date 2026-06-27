import logging
from datetime import datetime, timezone
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.core.websockets import manager
from app.models.attendance_record import AttendanceRecord
from app.models.user import User
from app.utils.geofencing import calculate_distance

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/check-in",
    response_model=schemas.AttendanceRecord,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a student check-in",
    description=(
        "Validates a student's check-in attempt using their current GPS location and the session code. "
        "Verifies session expiration, departmental compliance, and geofence radius restrictions. "
        "On success, creates an attendance record and triggers a live WebSocket update for the lecturer."
    ),
    responses={
        201: {
            "description": "Success - Attendance successfully verified and recorded."
        },
        400: {
            "description": (
                "Bad Request - Validation failed. Potential reasons: \n"
                "1. The attendance session has expired or is inactive. \n"
                "2. The student is outside the allowed geofenced radius. \n"
                "3. The student does not belong to the correct department for this course."
            )
        },
        401: {
            "description": "Unauthorized - Missing or invalid Bearer JWT security token."
        },
        403: {
            "description": "Forbidden - Only users with the 'Student' role can check into a session."
        },
        404: {
            "description": "Not Found - The provided Session Code does not match any active lecture."
        }
    }
)
def check_in(
    *,
    db: Session = Depends(deps.get_db),
    background_tasks: BackgroundTasks,
    payload: schemas.AttendanceCheckIn,
    current_user: User = Depends(deps.require_student),
) -> Any:
    """Mark attendance by submitting the session code shown by the lecturer.

    Fails if the code is invalid, the window has closed/expired, or the
    student has already checked in to that session.
    """
    student = crud.student.get(db, current_user.id)
    if not student:
        logger.warning(
            f"Check-in failed for user {current_user.id}: Student profile not found",
            extra={
                "student_id": current_user.id,
                "session_code": payload.session_code,
                "latitude": payload.latitude,
                "longitude": payload.longitude,
                "validation_outcome": "INVALID_STUDENT",
            },
        )
        raise HTTPException(status_code=404, detail="Student profile not found.")

    session = crud.attendance_session.get_by_code(db, session_code=payload.session_code)
    if not session:
        logger.warning(
            f"Check-in failed for student {student.user_id}: Invalid session code {payload.session_code}",
            extra={
                "student_id": student.user_id,
                "session_code": payload.session_code,
                "latitude": payload.latitude,
                "longitude": payload.longitude,
                "validation_outcome": "INVALID_CODE",
            },
        )
        raise HTTPException(status_code=404, detail="Invalid session code.")

    check_time = payload.check_in_time or datetime.now(timezone.utc)
    if check_time.tzinfo is None:
        check_time = check_time.replace(tzinfo=timezone.utc)

    session_expires_at = session.expires_at
    if session_expires_at.tzinfo is None:
        session_expires_at = session_expires_at.replace(tzinfo=timezone.utc)

    # If the check_in_time is after the session expired, reject it.
    # We do NOT reject based purely on session.status == "COMPLETED" because a lecturer 
    # might have closed the session while the student was still offline trying to sync.
    if check_time > session_expires_at:
        logger.warning(
            f"Check-in failed for student {student.user_id}: Check-in time {check_time} is past expiration {session_expires_at}",
            extra={
                "student_id": student.user_id,
                "session_id": session.id,
                "session_code": payload.session_code,
                "validation_outcome": "EXPIRED_CODE",
            },
        )
        raise HTTPException(
            status_code=400, detail="This attendance session was closed or expired at the time of your check-in."
        )

    existing = crud.attendance_record.get_by_session_and_student(
        db, session_id=session.id, student_id=student.user_id
    )
    if existing:
        logger.warning(
            f"Check-in failed for student {student.user_id}: Already checked in to session {session.id}",
            extra={
                "student_id": student.user_id,
                "session_id": session.id,
                "session_code": payload.session_code,
                "latitude": payload.latitude,
                "longitude": payload.longitude,
                "validation_outcome": "ALREADY_CHECKED_IN",
            },
        )
        raise HTTPException(
            status_code=400, detail="You have already checked in to this session."
        )

    if session.geofencing_enabled:
        if payload.latitude is None or payload.longitude is None:
            logger.warning(
                f"Check-in failed for student {student.user_id} on session {session.id}: Missing coordinates",
                extra={
                    "student_id": student.user_id,
                    "session_id": session.id,
                    "session_code": payload.session_code,
                    "latitude": payload.latitude,
                    "longitude": payload.longitude,
                    "validation_outcome": "MISSING_COORDINATES",
                },
            )
            raise HTTPException(
                status_code=400,
                detail="Geofencing is enabled. Location coordinates are required for check-in.",
            )
        distance = calculate_distance(
            payload.latitude, payload.longitude, session.latitude, session.longitude
        )
        if distance > (session.radius_meters or 50):
            logger.warning(
                f"Check-in failed for student {student.user_id} on session {session.id}: "
                f"Proximity violation ({distance:.1f}m > {session.radius_meters or 50}m)",
                extra={
                    "student_id": student.user_id,
                    "session_id": session.id,
                    "session_code": payload.session_code,
                    "latitude": payload.latitude,
                    "longitude": payload.longitude,
                    "distance": distance,
                    "radius_meters": session.radius_meters or 50,
                    "validation_outcome": "GEOPROXIMITY_VIOLATION",
                },
            )
            raise HTTPException(
                status_code=400,
                detail=f"Check-in failed. You are outside the designated area "
                f"({distance:.1f}m > {session.radius_meters or 50}m).",
            )

    record = AttendanceRecord(
        session_id=session.id,
        student_id=student.user_id,
        check_in_time=check_time,
        latitude=payload.latitude,
        longitude=payload.longitude,
        status="PRESENT",
    )
    try:
        db.add(record)
        db.commit()
        db.refresh(record)
    except IntegrityError:
        db.rollback()
        existing = crud.attendance_record.get_by_session_and_student(
            db, session_id=session.id, student_id=student.user_id
        )
        if existing:
            logger.warning(
                f"Check-in failed for student {student.user_id}: Already "
                f"checked in to session {session.id} (concurrency match)",
                extra={
                    "student_id": student.user_id,
                    "session_id": session.id,
                    "session_code": payload.session_code,
                    "latitude": payload.latitude,
                    "longitude": payload.longitude,
                    "validation_outcome": "ALREADY_CHECKED_IN",
                },
            )
            raise HTTPException(
                status_code=400, detail="You have already checked in to this session."
            )
        raise

    logger.info(
        f"Check-in successful for student {student.user_id} on session {session.id}",
        extra={
            "student_id": student.user_id,
            "session_id": session.id,
            "session_code": payload.session_code,
            "latitude": payload.latitude,
            "longitude": payload.longitude,
            "validation_outcome": "SUCCESS",
        },
    )

    # Broadcast to WebSocket
    record_dict = jsonable_encoder(record)
    # Since pydantic jsonable_encoder might not format fields exactly like schemas.AttendanceRecord dump,
    # let's validate it via schema first to ensure exact JSON match expected by clients
    record_schema = schemas.AttendanceRecord.model_validate(record)
    record_dict = jsonable_encoder(record_schema)

    background_tasks.add_task(
        manager.broadcast_to_session, str(session.id), record_dict
    )

    return record


@router.get(
    "/me",
    response_model=List[schemas.AttendanceHistoryRecord],
    summary="List my attendance records (student)",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized (Student only)"}
    }
)
def read_my_attendance(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.require_student),
) -> Any:
    """List the calling student's own attendance records."""
    records = crud.attendance_record.get_multi_by_student(
        db, student_id=current_user.id, skip=skip, limit=limit
    )
    result = []
    for r in records:
        schema = schemas.AttendanceHistoryRecord.model_validate(r)
        if r.attendance_session and r.attendance_session.course_assignment and r.attendance_session.course_assignment.course:
            schema.course_code = r.attendance_session.course_assignment.course.course_code
            schema.course_title = r.attendance_session.course_assignment.course.title
        result.append(schema)
    return result
