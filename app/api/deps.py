from typing import Generator, List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import crud
from app.core.security import ACCESS_TOKEN_TYPE, decode_token
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User

# Points Swagger's "Authorize" button at the login endpoint so the
# interactive docs can obtain and attach a bearer token automatically.
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None or payload.get("type") != ACCESS_TOKEN_TYPE:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = crud.user.get(db, id=user_id)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user


class RoleChecker:
    """Dependency that allows the request only for the given roles."""

    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user does not have enough privileges for this action.",
            )
        return current_user


# Convenience role guards.
require_admin = RoleChecker(["ADMIN"])
require_lecturer = RoleChecker(["LECTURER"])
require_student = RoleChecker(["STUDENT"])
require_staff = RoleChecker(["ADMIN", "LECTURER"])
