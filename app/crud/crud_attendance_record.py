from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.attendance_record import AttendanceRecord
from app.schemas.attendance_record import (
    AttendanceRecordCreate,
    AttendanceRecordUpdate,
)


class CRUDAttendanceRecord(
    CRUDBase[AttendanceRecord, AttendanceRecordCreate, AttendanceRecordUpdate]
):
    def get_by_session_and_student(
        self, db: Session, *, session_id: UUID, student_id: UUID
    ) -> Optional[AttendanceRecord]:
        return (
            db.query(AttendanceRecord)
            .filter(
                AttendanceRecord.session_id == session_id,
                AttendanceRecord.student_id == student_id,
            )
            .first()
        )

    def get_multi_by_session(
        self, db: Session, *, session_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[AttendanceRecord]:
        return (
            db.query(AttendanceRecord)
            .filter(AttendanceRecord.session_id == session_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_paginated_by_student(
        self, db: Session, *, student_id: UUID, skip: int = 0, limit: int = 100
    ) -> tuple[List[AttendanceRecord], int]:
        from app.models.attendance_session import AttendanceSession
        from app.models.course_assignment import CourseAssignment
        
        base_query = db.query(AttendanceRecord).filter(AttendanceRecord.student_id == student_id)
        total = base_query.count()
        
        items = (
            base_query
            .options(
                joinedload(AttendanceRecord.attendance_session)
                .joinedload(AttendanceSession.course_assignment)
                .joinedload(CourseAssignment.course)
            )
            .order_by(AttendanceRecord.check_in_time.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return items, total


attendance_record = CRUDAttendanceRecord(AttendanceRecord)
