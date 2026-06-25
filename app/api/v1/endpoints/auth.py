import logging
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
    verify_password,
)
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


def _build_login_response(user: User) -> schemas.LoginResponse:
    return schemas.LoginResponse(
        access_token=create_access_token(user.id, user.role),
        refresh_token=create_refresh_token(user.id, user.role),
        user=schemas.User.model_validate(user),
    )


@router.post(
    "/login",
    response_model=schemas.LoginResponse,
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
        logger.warning(f"Login failed: Incorrect email or password for {payload.email}", extra={"email": payload.email, "action": "login_failed_credentials"})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not crud.user.is_active(user):
        logger.warning(f"Login failed: Inactive user {payload.email}", extra={"email": payload.email, "user_id": user.id, "action": "login_failed_inactive"})
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    crud.user.touch_last_login(db, user=user)
    logger.info(f"Login successful for user {user.id}", extra={"email": user.email, "user_id": user.id, "action": "login_success"})
    return _build_login_response(user)


@router.post(
    "/refresh",
    response_model=schemas.LoginResponse,
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
        logger.warning("Token refresh failed: User not found or inactive", extra={"action": "refresh_failed_user"})
        raise invalid

    logger.info(f"Token refreshed for user {user.id}", extra={"user_id": user.id, "action": "refresh_success"})
    return _build_login_response(user)


@router.post(
    "/register",
    response_model=schemas.LoginResponse,
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
    logger.info(f"New student registered: {student.user_id}", extra={"user_id": student.user_id, "email": body.email, "matric_number": body.matric_number, "action": "register_student"})
    return _build_login_response(student.user)


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


@router.patch(
    "/me",
    response_model=schemas.User,
    summary="Update current logged-in user profile",
)
def update_me(
    *,
    db: Session = Depends(deps.get_db),
    body: schemas.ProfileUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Update name, email, etc. for the logged-in user."""
    if body.email and body.email != current_user.email:
        existing_user = crud.user.get_by_email(db, email=body.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists.",
            )
    updated_user = crud.user.update(db, db_obj=current_user, obj_in=body)
    logger.info(f"User {current_user.id} updated profile", extra={"user_id": current_user.id, "action": "update_profile"})
    return updated_user


@router.post(
    "/change-password",
    summary="Change the current user's password",
)
def change_password(
    body: schemas.PasswordUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Update password for the logged-in user."""
    if not verify_password(body.old_password, current_user.password_hash):
        logger.warning(f"Password change failed for user {current_user.id}", extra={"user_id": current_user.id, "action": "password_change_failed"})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password",
        )
    crud.user.update(db, db_obj=current_user, obj_in={"password": body.new_password})
    logger.info(f"Password changed for user {current_user.id}", extra={"user_id": current_user.id, "action": "password_change_success"})
    return {"message": "Password updated successfully"}
