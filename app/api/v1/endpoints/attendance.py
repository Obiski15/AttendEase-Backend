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
    summary="Check in to an attendance session (student)",
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

    if not crud.attendance_session.is_open(session):
        logger.warning(
            f"Check-in failed for student {student.user_id}: Session {session.id} is closed or expired",
            extra={
                "student_id": student.user_id,
                "session_id": session.id,
                "session_code": payload.session_code,
                "latitude": payload.latitude,
                "longitude": payload.longitude,
                "validation_outcome": "EXPIRED_CODE",
            },
        )
        raise HTTPException(
            status_code=400, detail="This attendance session is closed or expired."
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
        check_in_time=datetime.now(timezone.utc),
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
