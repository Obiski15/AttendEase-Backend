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
    response_model=List[schemas.Course],
    summary="List courses",
    responses={
        401: {"description": "Not authenticated"}
    }
)
def read_courses(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records to return"),
    _: User = Depends(deps.get_current_active_user),
) -> Any:
    """List all courses. Any authenticated user."""
    return crud.course.get_multi(db, skip=skip, limit=limit)


@router.post(
    "/",
    response_model=schemas.Course,
    status_code=status.HTTP_201_CREATED,
    summary="Create a course (admin)",
    responses={
        400: {"description": "Course code already exists"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized (Admin only)"},
        404: {"description": "Department not found"}
    }
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
    course = crud.course.create(db=db, obj_in=course_in)
    logger.info(f"Course {course.id} created", extra={"course_id": course.id, "course_code": course.course_code, "department_id": course.department_id, "action": "create_course"})
    return course


@router.get(
    "/{course_id}",
    response_model=schemas.Course,
    summary="Get a course",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Course not found"}
    }
)
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
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized (Admin only)"},
        404: {"description": "Course not found"}
    }
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
    updated_course = crud.course.update(db=db, db_obj=course, obj_in=course_in)
    logger.info(f"Course {course_id} updated", extra={"course_id": course_id, "action": "update_course"})
    return updated_course


@router.delete(
    "/{course_id}",
    response_model=schemas.Course,
    summary="Delete a course (admin)",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized (Admin only)"},
        404: {"description": "Course not found"}
    }
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
    deleted_course = crud.course.remove(db=db, id=course_id)
    logger.info(f"Course {course_id} deleted", extra={"course_id": course_id, "action": "delete_course"})
    return deleted_course
