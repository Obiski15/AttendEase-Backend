from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

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

    def get_multi_by_student(
        self, db: Session, *, student_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[AttendanceRecord]:
        return (
            db.query(AttendanceRecord)
            .filter(AttendanceRecord.student_id == student_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


attendance_record = CRUDAttendanceRecord(AttendanceRecord)
