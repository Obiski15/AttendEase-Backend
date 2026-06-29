import secrets
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.attendance_session import AttendanceSession
from app.schemas.attendance_session import (
    AttendanceSessionCreate,
    AttendanceSessionUpdate,
)


def _generate_code() -> str:
    # Short, human-typable, unambiguous uppercase code (e.g. "A3F9K2").
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(secrets.choice(alphabet) for _ in range(6))


class CRUDAttendanceSession(
    CRUDBase[AttendanceSession, AttendanceSessionCreate, AttendanceSessionUpdate]
):
    def get_by_code(
        self, db: Session, *, session_code: str
    ) -> Optional[AttendanceSession]:
        return (
            db.query(AttendanceSession)
            .filter(AttendanceSession.session_code == session_code)
            .first()
        )



    def get_paginated_by_assignment(
        self,
        db: Session,
        *,
        course_assignment_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[AttendanceSession], int]:
        base_query = db.query(AttendanceSession).filter(AttendanceSession.course_assignment_id == course_assignment_id)
        total = base_query.count()
        items = base_query.offset(skip).limit(limit).all()
        return items, total




        

    def get_paginated_by_lecturer(
        self, db: Session, *, lecturer_id: UUID, skip: int = 0, limit: int = 100
    ) -> tuple[List[AttendanceSession], int]:
        from app.models.course_assignment import CourseAssignment

        base_query = (
            db.query(AttendanceSession)
            .join(
                CourseAssignment,
                AttendanceSession.course_assignment_id == CourseAssignment.id,
            )
            .filter(CourseAssignment.lecturer_id == lecturer_id)
        )
        total = base_query.count()
        items = (
            base_query
            .order_by(AttendanceSession.start_time.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return items, total

    def open_session(
        self, db: Session, *, obj_in: AttendanceSessionCreate
    ) -> AttendanceSession:
        now = datetime.now(timezone.utc)
        start_time = obj_in.start_time or now
        expires_at = obj_in.expires_at or (
            start_time + timedelta(minutes=obj_in.duration_minutes or 60)
        )

        # Ensure a unique session code.
        code = obj_in.session_code
        if code is None:
            while code is None or self.get_by_code(db, session_code=code):
                code = _generate_code()
        else:
            # If client provides code, verify no collision exists just in case
            if self.get_by_code(db, session_code=code):
                raise ValueError("Session code collision")

        kwargs = {
            "course_assignment_id": obj_in.course_assignment_id,
            "session_date": obj_in.session_date or date.today(),
            "start_time": start_time,
            "expires_at": expires_at,
            "session_code": code,
            "status": "ACTIVE",
            "geofencing_enabled": obj_in.geofencing_enabled or False,
            "latitude": obj_in.latitude,
            "longitude": obj_in.longitude,
            "radius_meters": obj_in.radius_meters or 50,
        }
        if obj_in.id is not None:
            kwargs["id"] = obj_in.id

        db_obj = AttendanceSession(**kwargs)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def is_open(self, session: AttendanceSession) -> bool:
        expires_at = session.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return session.status == "ACTIVE" and expires_at > datetime.now(timezone.utc)

    def close(self, db: Session, *, db_obj: AttendanceSession) -> AttendanceSession:
        db_obj.status = "COMPLETED"
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


attendance_session = CRUDAttendanceSession(AttendanceSession)
