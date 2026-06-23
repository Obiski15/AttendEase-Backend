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
    response_model=List[schemas.CourseAssignment],
    summary="List course assignments",
)
def read_course_assignments(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """List course assignments. Lecturers see only their own; admins see all."""
    if current_user.role == "LECTURER":
        return crud.course_assignment.get_multi_by_lecturer(
            db, lecturer_id=current_user.id, skip=skip, limit=limit
        )
    if current_user.role == "ADMIN":
        return crud.course_assignment.get_multi(db, skip=skip, limit=limit)
    raise HTTPException(status_code=403, detail="Not enough privileges.")


@router.post(
    "/",
    response_model=schemas.CourseAssignment,
    status_code=status.HTTP_201_CREATED,
    summary="Create a course assignment (admin)",
)
def create_course_assignment(
    *,
    db: Session = Depends(deps.get_db),
    assignment_in: schemas.CourseAssignmentCreate,
    _: User = Depends(deps.require_admin),
) -> Any:
    """Assign a lecturer to teach a course in an academic session. Admin only."""
    if not crud.course.get(db, id=assignment_in.course_id):
        raise HTTPException(status_code=404, detail="Course not found.")
    if not crud.lecturer.get(db, assignment_in.lecturer_id):
        raise HTTPException(status_code=404, detail="Lecturer not found.")
    if not crud.academic_session.get(db, id=assignment_in.academic_session_id):
        raise HTTPException(status_code=404, detail="Academic session not found.")
    return crud.course_assignment.create(db=db, obj_in=assignment_in)


@router.get(
    "/{assignment_id}",
    response_model=schemas.CourseAssignment,
    summary="Get a course assignment",
)
def read_course_assignment(
    *,
    db: Session = Depends(deps.get_db),
    assignment_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    assignment = crud.course_assignment.get(db=db, id=assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Course assignment not found")
    if current_user.role == "LECTURER" and assignment.lecturer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough privileges.")
    if current_user.role == "STUDENT":
        raise HTTPException(status_code=403, detail="Not enough privileges.")
    return assignment


@router.delete(
    "/{assignment_id}",
    response_model=schemas.CourseAssignment,
    summary="Delete a course assignment (admin)",
)
def delete_course_assignment(
    *,
    db: Session = Depends(deps.get_db),
    assignment_id: UUID,
    _: User = Depends(deps.require_admin),
) -> Any:
    assignment = crud.course_assignment.get(db=db, id=assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Course assignment not found")
    return crud.course_assignment.remove(db=db, id=assignment_id)
