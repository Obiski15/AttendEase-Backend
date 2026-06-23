from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.core.security import (
    REFRESH_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User

router = APIRouter()


def _issue_tokens(user: User) -> schemas.Token:
    return schemas.Token(
        access_token=create_access_token(user.id, user.role),
        refresh_token=create_refresh_token(user.id, user.role),
    )


@router.post(
    "/login",
    response_model=schemas.Token,
    summary="Log in and obtain tokens",
)
def login(
    payload: schemas.LoginPayload,
    db: Session = Depends(deps.get_db),
) -> Any:
    """Authenticate with email and password.

    Returns an access_token and a refresh_token. Send the access token as
    `Authorization: Bearer <token>` on every request.
    """
    user = crud.user.authenticate(db, email=payload.email, password=payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not crud.user.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    crud.user.touch_last_login(db, user=user)
    return _issue_tokens(user)


@router.post(
    "/refresh",
    response_model=schemas.Token,
    summary="Refresh the access token",
)
def refresh_token(
    body: schemas.TokenRefresh,
    db: Session = Depends(deps.get_db),
) -> Any:
    """Exchange a valid refresh token for a new token pair.

    Call this when the access token expires to keep the user logged in.
    """
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )
    payload = decode_token(body.refresh_token)
    if payload is None or payload.get("type") != REFRESH_TOKEN_TYPE:
        raise invalid

    user = crud.user.get(db, id=payload.get("sub"))
    if user is None or not crud.user.is_active(user):
        raise invalid

    return _issue_tokens(user)


@router.post(
    "/register",
    response_model=schemas.Token,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new student (self-service)",
)
def register(
    body: schemas.StudentRegister,
    db: Session = Depends(deps.get_db),
) -> Any:
    """Public sign-up for students. Creates the account and returns a token pair."""
    if crud.user.get_by_email(db, email=body.email):
        raise HTTPException(
            status_code=400, detail="A user with this email already exists."
        )
    if crud.student.get_by_matric(db, matric_number=body.matric_number):
        raise HTTPException(
            status_code=400, detail="This matric number is already registered."
        )
    if not crud.department.get(db, id=body.department_id):
        raise HTTPException(status_code=404, detail="Department not found.")

    student = crud.student.create_with_user(db, obj_in=body)
    return _issue_tokens(student.user)


@router.get(
    "/me",
    response_model=schemas.User,
    summary="Get the current logged-in user",
)
def read_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Return the profile of the currently authenticated user."""
    return current_user
