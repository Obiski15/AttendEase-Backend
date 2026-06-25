from typing import Any, List, Optional, Union
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.crud.base import CRUDBase
from app.models.student import Student
from app.models.user import User
from app.schemas.student import StudentCreate, StudentUpdate


class CRUDStudent(CRUDBase[Student, StudentCreate, StudentUpdate]):
    # Student's primary key is user_id (shared with users), not `id`.
    def get(self, db: Session, user_id: UUID) -> Optional[Student]:
        return db.query(Student).filter(Student.user_id == user_id).first()

    def get_by_matric(self, db: Session, *, matric_number: str) -> Optional[Student]:
        return db.query(Student).filter(Student.matric_number == matric_number).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Student]:
        return db.query(Student).offset(skip).limit(limit).all()

    def create_with_user(
        self, db: Session, *, obj_in: Union[StudentCreate, Any]
    ) -> Student:
        """Provision the User account and the Student profile together."""
        user = User(
            email=obj_in.email,
            password_hash=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            role="STUDENT",
            status="ACTIVE",
        )
        db.add(user)
        db.flush()  # assign user.id without committing yet

        student = Student(
            user_id=user.id,
            student_id=obj_in.student_id,
            matric_number=obj_in.matric_number,
            department_id=obj_in.department_id,
            level=obj_in.level,
        )
        db.add(student)
        db.commit()
        db.refresh(student)
        return student

    def remove(self, db: Session, *, user_id: UUID) -> Optional[Student]:
        # Deleting the user cascades to the student profile.
        user = db.get(User, user_id)
        if user:
            db.delete(user)
            db.commit()
        return None


student = CRUDStudent(Student)
