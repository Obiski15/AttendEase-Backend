from typing import List
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.course_assignment import CourseAssignment
from app.models.lecturer import Lecturer
from app.schemas.course_assignment import (
    CourseAssignmentCreate,
    CourseAssignmentUpdate,
)


class CRUDCourseAssignment(
    CRUDBase[CourseAssignment, CourseAssignmentCreate, CourseAssignmentUpdate]
):
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[CourseAssignment]:
        return (
            db.query(CourseAssignment)
            .options(
                joinedload(CourseAssignment.course),
                joinedload(CourseAssignment.lecturer).joinedload(Lecturer.user),
                joinedload(CourseAssignment.academic_session)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_lecturer(
        self, db: Session, *, lecturer_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[CourseAssignment]:
        return (
            db.query(CourseAssignment)
            .options(
                joinedload(CourseAssignment.course),
                joinedload(CourseAssignment.lecturer).joinedload(Lecturer.user),
                joinedload(CourseAssignment.academic_session)
            )
            .filter(CourseAssignment.lecturer_id == lecturer_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


course_assignment = CRUDCourseAssignment(CourseAssignment)
