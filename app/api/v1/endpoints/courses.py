from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[schemas.Course], summary="List courses")
def read_courses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    _: User = Depends(deps.get_current_active_user),
) -> Any:
    """List all courses. Any authenticated user."""
    return crud.course.get_multi(db, skip=skip, limit=limit)


@router.post(
    "/",
    response_model=schemas.Course,
    status_code=status.HTTP_201_CREATED,
    summary="Create a course (admin)",
)
def create_course(
    *,
    db: Session = Depends(deps.get_db),
    course_in: schemas.CourseCreate,
    _: User = Depends(deps.require_admin),
) -> Any:
    """Create a course. Admin only."""
    if crud.course.get_by_code(db, course_code=course_in.course_code):
        raise HTTPException(
            status_code=400, detail="A course with this code already exists."
        )
    if not crud.department.get(db, id=course_in.department_id):
        raise HTTPException(status_code=404, detail="Department not found.")
    return crud.course.create(db=db, obj_in=course_in)


@router.get("/{course_id}", response_model=schemas.Course, summary="Get a course")
def read_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: UUID,
    _: User = Depends(deps.get_current_active_user),
) -> Any:
    course = crud.course.get(db=db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.patch(
    "/{course_id}",
    response_model=schemas.Course,
    summary="Update a course (admin)",
)
def update_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: UUID,
    course_in: schemas.CourseUpdate,
    _: User = Depends(deps.require_admin),
) -> Any:
    course = crud.course.get(db=db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return crud.course.update(db=db, db_obj=course, obj_in=course_in)


@router.delete(
    "/{course_id}",
    response_model=schemas.Course,
    summary="Delete a course (admin)",
)
def delete_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: UUID,
    _: User = Depends(deps.require_admin),
) -> Any:
    course = crud.course.get(db=db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return crud.course.remove(db=db, id=course_id)
