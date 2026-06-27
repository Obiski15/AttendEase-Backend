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


from fastapi import APIRouter, Depends, HTTPException, status, Query

@router.get(
    "/",
    response_model=List[schemas.Department],
    summary="List departments",
    responses={
        401: {"description": "Not authenticated"}
    }
)
def read_departments(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records to return"),
    _: User = Depends(deps.get_current_active_user),
) -> Any:
    """List all departments. Any authenticated user."""
    return crud.department.get_multi(db, skip=skip, limit=limit)


@router.post(
    "/",
    response_model=schemas.Department,
    status_code=status.HTTP_201_CREATED,
    summary="Create a department (admin)",
    responses={
        400: {"description": "Department name already exists"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized (Admin only)"}
    }
)
def create_department(
    *,
    db: Session = Depends(deps.get_db),
    department_in: schemas.DepartmentCreate,
    _: User = Depends(deps.require_admin),
) -> Any:
    """Create a department. Admin only."""
    if crud.department.get_by_name(db, name=department_in.name):
        raise HTTPException(
            status_code=400, detail="A department with this name already exists."
        )
    department = crud.department.create(db=db, obj_in=department_in)
    logger.info(f"Department {department.id} created", extra={"department_id": department.id, "name": department.name, "action": "create_department"})
    return department


@router.get(
    "/{department_id}",
    response_model=schemas.Department,
    summary="Get a department",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Department not found"}
    }
)
def read_department(
    *,
    db: Session = Depends(deps.get_db),
    department_id: UUID,
    _: User = Depends(deps.get_current_active_user),
) -> Any:
    department = crud.department.get(db=db, id=department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


@router.patch(
    "/{department_id}",
    response_model=schemas.Department,
    summary="Update a department (admin)",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized (Admin only)"},
        404: {"description": "Department not found"}
    }
)
def update_department(
    *,
    db: Session = Depends(deps.get_db),
    department_id: UUID,
    department_in: schemas.DepartmentUpdate,
    _: User = Depends(deps.require_admin),
) -> Any:
    department = crud.department.get(db=db, id=department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    updated_department = crud.department.update(db=db, db_obj=department, obj_in=department_in)
    logger.info(f"Department {department_id} updated", extra={"department_id": department_id, "action": "update_department"})
    return updated_department


@router.delete(
    "/{department_id}",
    response_model=schemas.Department,
    summary="Delete a department (admin)",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized (Admin only)"},
        404: {"description": "Department not found"}
    }
)
def delete_department(
    *,
    db: Session = Depends(deps.get_db),
    department_id: UUID,
    _: User = Depends(deps.require_admin),
) -> Any:
    department = crud.department.get(db=db, id=department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    deleted_department = crud.department.remove(db=db, id=department_id)
    logger.info(f"Department {department_id} deleted", extra={"department_id": department_id, "action": "delete_department"})
    return deleted_department
