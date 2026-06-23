from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.models.user import User

router = APIRouter()


@router.get(
    "/",
    response_model=List[schemas.User],
    summary="List users (admin)",
)
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    _: User = Depends(deps.require_admin),
) -> Any:
    """Retrieve all users. Admin only."""
    return crud.user.get_multi(db, skip=skip, limit=limit)


@router.post(
    "/",
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user (admin)",
)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    _: User = Depends(deps.require_admin),
) -> Any:
    """Create a new user with an explicit role (e.g. another ADMIN). Admin only."""
    if crud.user.get_by_email(db, email=user_in.email):
        raise HTTPException(status_code=400, detail="The user with this email already exists.")
    return crud.user.create(db=db, obj_in=user_in)


@router.get(
    "/{user_id}",
    response_model=schemas.User,
    summary="Get a user by ID (admin)",
)
def read_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: UUID,
    _: User = Depends(deps.require_admin),
) -> Any:
    """Get a single user by ID. Admin only."""
    user = crud.user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch(
    "/{user_id}",
    response_model=schemas.User,
    summary="Update a user (admin)",
)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: UUID,
    user_in: schemas.UserUpdate,
    _: User = Depends(deps.require_admin),
) -> Any:
    """Update a user's fields (including password). Admin only."""
    user = crud.user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.user.update(db=db, db_obj=user, obj_in=user_in)


@router.delete(
    "/{user_id}",
    response_model=schemas.User,
    summary="Deactivate a user (admin)",
)
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: UUID,
    _: User = Depends(deps.require_admin),
) -> Any:
    """Soft-delete (deactivate) a user. Admin only."""
    user = crud.user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.user.soft_delete(db=db, user=user)
