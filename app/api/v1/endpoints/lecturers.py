import logging
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/",
    response_model=schemas.PaginatedResponse[schemas.Lecturer],
    summary="List lecturers (admin)",
)
def read_lecturers(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    search: str | None = Query(None, description="Search term for name, email, or staff ID"),
    _: User = Depends(deps.require_admin),
) -> Any:
    """List lecturers. Admin only."""
    items, total = crud.lecturer.get_paginated(db, skip=skip, limit=limit, search=search)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.post(
    "/",
    response_model=schemas.Lecturer,
    status_code=status.HTTP_201_CREATED,
    summary="Create a lecturer (admin)",
)
def create_lecturer(
    *,
    db: Session = Depends(deps.get_db),
    lecturer_in: schemas.LecturerCreate,
    _: User = Depends(deps.require_admin),
) -> Any:
    """Provision a lecturer account + profile. Admin only."""
    if crud.user.get_by_email(db, email=lecturer_in.email):
        raise HTTPException(
            status_code=400, detail="A user with this email already exists."
        )
    if crud.lecturer.get_by_staff_id(db, staff_id=lecturer_in.staff_id):
        raise HTTPException(
            status_code=400, detail="This staff ID is already registered."
        )
    if not crud.department.get(db, id=lecturer_in.department_id):
        raise HTTPException(status_code=404, detail="Department not found.")
    lecturer = crud.lecturer.create_with_user(db=db, obj_in=lecturer_in)
    logger.info(f"Lecturer {lecturer.user_id} created by admin", extra={"target_user_id": lecturer.user_id, "staff_id": lecturer.staff_id, "action": "create_lecturer"})
    return lecturer


@router.get(
    "/{user_id}",
    response_model=schemas.Lecturer,
    summary="Get a lecturer",
)
def read_lecturer(
    *,
    db: Session = Depends(deps.get_db),
    user_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get a lecturer profile. Admin, or the lecturer viewing themselves."""
    if current_user.role != "ADMIN" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough privileges.")
    lecturer = crud.lecturer.get(db, user_id)
    if not lecturer:
        raise HTTPException(status_code=404, detail="Lecturer not found")
    return lecturer


@router.patch(
    "/{user_id}",
    response_model=schemas.Lecturer,
    summary="Update a lecturer (admin)",
)
def update_lecturer(
    *,
    db: Session = Depends(deps.get_db),
    user_id: UUID,
    lecturer_in: schemas.LecturerUpdate,
    _: User = Depends(deps.require_admin),
) -> Any:
    lecturer = crud.lecturer.get(db, user_id)
    if not lecturer:
        raise HTTPException(status_code=404, detail="Lecturer not found")
    updated_lecturer = crud.lecturer.update(db=db, db_obj=lecturer, obj_in=lecturer_in)
    logger.info(f"Lecturer {user_id} updated by admin", extra={"target_user_id": user_id, "action": "update_lecturer_admin"})
    return updated_lecturer


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a lecturer (admin)",
)
def delete_lecturer(
    *,
    db: Session = Depends(deps.get_db),
    user_id: UUID,
    _: User = Depends(deps.require_admin),
) -> None:
    """Delete a lecturer and their user account. Admin only."""
    lecturer = crud.lecturer.get(db, user_id)
    if not lecturer:
        raise HTTPException(status_code=404, detail="Lecturer not found")
    crud.lecturer.remove(db=db, user_id=user_id)
    logger.info(f"Lecturer {user_id} deleted by admin", extra={"target_user_id": user_id, "action": "delete_lecturer"})
