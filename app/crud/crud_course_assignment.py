from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.course_assignment import CourseAssignment
from app.schemas.course_assignment import (
    CourseAssignmentCreate,
    CourseAssignmentUpdate,
)


class CRUDCourseAssignment(
    CRUDBase[CourseAssignment, CourseAssignmentCreate, CourseAssignmentUpdate]
):
    def get_multi_by_lecturer(
        self, db: Session, *, lecturer_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[CourseAssignment]:
        return (
            db.query(CourseAssignment)
            .filter(CourseAssignment.lecturer_id == lecturer_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


course_assignment = CRUDCourseAssignment(CourseAssignment)
