from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.crud.base import CRUDBase
from app.models.lecturer import Lecturer
from app.models.user import User
from app.schemas.lecturer import LecturerCreate, LecturerUpdate


class CRUDLecturer(CRUDBase[Lecturer, LecturerCreate, LecturerUpdate]):
    # Lecturer's primary key is user_id (shared with users), not `id`.
    def get(self, db: Session, user_id: UUID) -> Optional[Lecturer]:
        return db.query(Lecturer).filter(Lecturer.user_id == user_id).first()

    def get_by_staff_id(self, db: Session, *, staff_id: str) -> Optional[Lecturer]:
        return db.query(Lecturer).filter(Lecturer.staff_id == staff_id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Lecturer]:
        return db.query(Lecturer).offset(skip).limit(limit).all()

    def create_with_user(self, db: Session, *, obj_in: LecturerCreate) -> Lecturer:
        """Provision the User account and the Lecturer profile together."""
        user = User(
            email=obj_in.email,
            password_hash=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            role="LECTURER",
            status="ACTIVE",
        )
        db.add(user)
        db.flush()

        lecturer = Lecturer(
            user_id=user.id,
            staff_id=obj_in.staff_id,
            department_id=obj_in.department_id,
        )
        db.add(lecturer)
        db.commit()
        db.refresh(lecturer)
        return lecturer

    def remove(self, db: Session, *, user_id: UUID) -> Optional[Lecturer]:
        user = db.get(User, user_id)
        if user:
            db.delete(user)
            db.commit()
        return None


lecturer = CRUDLecturer(Lecturer)
