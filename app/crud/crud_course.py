from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate


class CRUDCourse(CRUDBase[Course, CourseCreate, CourseUpdate]):
    def get_by_code(self, db: Session, *, course_code: str) -> Optional[Course]:
        return db.query(Course).filter(Course.course_code == course_code).first()


course = CRUDCourse(Course)
