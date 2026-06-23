from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            password_hash=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            role=obj_in.role,
            status=obj_in.status or "ACTIVE",
            profile_image_url=obj_in.profile_image_url,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]],
    ) -> User:
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        # Hash a new password if one was supplied, never store it raw.
        if update_data.get("password"):
            update_data["password_hash"] = get_password_hash(update_data.pop("password"))
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.status == "ACTIVE" and user.deleted_at is None

    def touch_last_login(self, db: Session, *, user: User) -> None:
        user.last_login = datetime.now(timezone.utc)
        db.add(user)
        db.commit()

    def soft_delete(self, db: Session, *, user: User) -> User:
        user.deleted_at = datetime.now(timezone.utc)
        user.status = "INACTIVE"
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


user = CRUDUser(User)
