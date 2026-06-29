from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate


class CRUDCourse(CRUDBase[Course, CourseCreate, CourseUpdate]):
    def get_by_code(self, db: Session, *, course_code: str) -> Optional[Course]:
        return db.query(Course).filter(Course.course_code == course_code).first()

    def _base_query(self, db: Session):
        from sqlalchemy.orm import joinedload
        from app.models.course_assignment import CourseAssignment
        from app.models.lecturer import Lecturer
        return db.query(Course).options(
            joinedload(Course.department),
            joinedload(Course.course_assignments).joinedload(CourseAssignment.lecturer).joinedload(Lecturer.user)
        )

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[Course]:
        return self._base_query(db).offset(skip).limit(limit).all()

    def get_paginated(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> tuple[list[Course], int]:
        query = self._base_query(db)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total


course = CRUDCourse(Course)
