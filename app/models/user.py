import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.lecturer import Lecturer
    from app.models.student import Student


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    full_name: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="ACTIVE")
    profile_image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    student_profile: Mapped[Optional["Student"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    lecturer_profile: Mapped[Optional["Lecturer"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
