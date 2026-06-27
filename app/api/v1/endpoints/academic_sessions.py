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
        session = crud.academic_session.create(db=db, obj_in=session_in)
        logger.info(f"Academic session {session.id} created", extra={"session_id": session.id, "name": session.name, "action": "create_academic_session"})
        return session
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
        updated_session = crud.academic_session.update(db=db, db_obj=session, obj_in=session_in)
        logger.info(f"Academic session {session_id} updated", extra={"session_id": session_id, "action": "update_academic_session"})
        return updated_session
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{session_id}/activate",
    response_model=schemas.AcademicSession,
    summary="Activate an academic session",
    description="Changes the status of a specific academic session to active. This session will be used as the current institutional framework for courses and attendance tracking. Restricted to IT Administrators.",
    responses={
        200: {"description": "Success - Academic session has been successfully activated"},
        401: {"description": "Unauthorized - Missing or invalid Bearer JWT token"},
        403: {"description": "Forbidden - Current user does not have Administrator privileges"},
        404: {"description": "Not Found - No academic session found with the provided session_id"}
    }
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
        activated_session = crud.academic_session.activate(db=db, db_obj=session)
        logger.info(f"Academic session {session_id} activated", extra={"session_id": session_id, "action": "activate_academic_session"})
        return activated_session
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
    deleted_session = crud.academic_session.remove(db=db, id=session_id)
    logger.info(f"Academic session {session_id} deleted", extra={"session_id": session_id, "action": "delete_academic_session"})
    return deleted_session
