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
    response_model=List[schemas.AcademicSession],
    summary="List academic sessions",
)
def read_academic_sessions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    _: User = Depends(deps.get_current_active_user),
) -> Any:
    """List all academic sessions / semesters. Any authenticated user."""
    return crud.academic_session.get_multi(db, skip=skip, limit=limit)


@router.post(
    "/",
    response_model=schemas.AcademicSession,
    status_code=status.HTTP_201_CREATED,
    summary="Create an academic session (admin)",
)
def create_academic_session(
    *,
    db: Session = Depends(deps.get_db),
    session_in: schemas.AcademicSessionCreate,
    _: User = Depends(deps.require_admin),
) -> Any:
    """Create an academic session. Admin only."""
    try:
        return crud.academic_session.create(db=db, obj_in=session_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{session_id}",
    response_model=schemas.AcademicSession,
    summary="Get an academic session",
)
def read_academic_session(
    *,
    db: Session = Depends(deps.get_db),
    session_id: UUID,
    _: User = Depends(deps.get_current_active_user),
) -> Any:
    session = crud.academic_session.get(db=db, id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Academic session not found")
    return session


@router.patch(
    "/{session_id}",
    response_model=schemas.AcademicSession,
    summary="Update an academic session (admin)",
)
def update_academic_session(
    *,
    db: Session = Depends(deps.get_db),
    session_id: UUID,
    session_in: schemas.AcademicSessionUpdate,
    _: User = Depends(deps.require_admin),
) -> Any:
    session = crud.academic_session.get(db=db, id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Academic session not found")
    try:
        return crud.academic_session.update(db=db, db_obj=session, obj_in=session_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{session_id}/activate",
    response_model=schemas.AcademicSession,
    summary="Activate an academic session (admin)",
)
def activate_academic_session(
    *,
    db: Session = Depends(deps.get_db),
    session_id: UUID,
    _: User = Depends(deps.require_admin),
) -> Any:
    """Mark a session as the active one; all others are deactivated. Admin only."""
    session = crud.academic_session.get(db=db, id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Academic session not found")
    try:
        return crud.academic_session.activate(db=db, db_obj=session)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{session_id}",
    response_model=schemas.AcademicSession,
    summary="Delete an academic session (admin)",
)
def delete_academic_session(
    *,
    db: Session = Depends(deps.get_db),
    session_id: UUID,
    _: User = Depends(deps.require_admin),
) -> Any:
    session = crud.academic_session.get(db=db, id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Academic session not found")
    return crud.academic_session.remove(db=db, id=session_id)
