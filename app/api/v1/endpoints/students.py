import logging
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/",
    response_model=schemas.PaginatedResponse[schemas.Student],
    summary="List students (admin/lecturer)",
)
def read_students(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    _: User = Depends(deps.require_staff),
) -> Any:
    """List students. Admin or lecturer."""
    items, total = crud.student.get_paginated(db, skip=skip, limit=limit)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.post(
    "/",
    response_model=schemas.Student,
    status_code=status.HTTP_201_CREATED,
    summary="Create a student (admin)",
)
def create_student(
    *,
    db: Session = Depends(deps.get_db),
    student_in: schemas.StudentCreate,
    _: User = Depends(deps.require_admin),
) -> Any:
    """Provision a student account + profile. Admin only."""
    if crud.user.get_by_email(db, email=student_in.email):
        raise HTTPException(
            status_code=400, detail="A user with this email already exists."
        )
    if crud.student.get_by_matric(db, matric_number=student_in.matric_number):
        raise HTTPException(
            status_code=400, detail="This matric number is already registered."
        )
    if not crud.department.get(db, id=student_in.department_id):
        raise HTTPException(status_code=404, detail="Department not found.")
    student = crud.student.create_with_user(db=db, obj_in=student_in)
    logger.info(f"Student {student.user_id} created by admin", extra={"target_user_id": student.user_id, "matric_number": student.matric_number, "action": "create_student"})
    return student


@router.get(
    "/{user_id}",
    response_model=schemas.Student,
    summary="Get a student",
)
def read_student(
    *,
    db: Session = Depends(deps.get_db),
    user_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get a student profile. Admin/lecturer, or the student viewing themselves."""
    if current_user.role not in ("ADMIN", "LECTURER") and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough privileges.")
    student = crud.student.get(db, user_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.patch(
    "/{user_id}",
    response_model=schemas.Student,
    summary="Update a student (admin)",
)
def update_student(
    *,
    db: Session = Depends(deps.get_db),
    user_id: UUID,
    student_in: schemas.StudentUpdate,
    _: User = Depends(deps.require_admin),
) -> Any:
    student = crud.student.get(db, user_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    updated_student = crud.student.update(db=db, db_obj=student, obj_in=student_in)
    logger.info(f"Student {user_id} updated by admin", extra={"target_user_id": user_id, "action": "update_student_admin"})
    return updated_student


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a student (admin)",
)
def delete_student(
    *,
    db: Session = Depends(deps.get_db),
    user_id: UUID,
    _: User = Depends(deps.require_admin),
) -> None:
    """Delete a student and their user account. Admin only."""
    student = crud.student.get(db, user_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    crud.student.remove(db=db, user_id=user_id)
    logger.info(f"Student {user_id} deleted by admin", extra={"target_user_id": user_id, "action": "delete_student"})
