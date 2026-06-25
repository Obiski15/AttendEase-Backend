from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[schemas.Department], summary="List departments")
def read_departments(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    _: User = Depends(deps.get_current_active_user),
) -> Any:
    """List all departments. Any authenticated user."""
    return crud.department.get_multi(db, skip=skip, limit=limit)


@router.post(
    "/",
    response_model=schemas.Department,
    status_code=status.HTTP_201_CREATED,
    summary="Create a department (admin)",
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
    return crud.department.create(db=db, obj_in=department_in)


@router.get(
    "/{department_id}", response_model=schemas.Department, summary="Get a department"
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
    return crud.department.update(db=db, db_obj=department, obj_in=department_in)


@router.delete(
    "/{department_id}",
    response_model=schemas.Department,
    summary="Delete a department (admin)",
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
    return crud.department.remove(db=db, id=department_id)
