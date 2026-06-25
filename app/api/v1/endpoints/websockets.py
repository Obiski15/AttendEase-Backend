import logging

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.core.security import decode_token, ACCESS_TOKEN_TYPE
from app.core.websockets import manager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/attendance/{session_id}")
async def websocket_attendance_endpoint(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(None),
    db: Session = Depends(deps.get_db),
):
    if not token:
        await websocket.close(code=1008, reason="Missing token")
        return

    # Verify the token
    try:
        payload = decode_token(token)
        if payload is None or payload.get("type") != ACCESS_TOKEN_TYPE:
            await websocket.close(code=1008, reason="Invalid token type")
            return

        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=1008, reason="Invalid token payload")
            return

        user = crud.user.get(db, id=user_id)
        if not user or user.role != "LECTURER":
            # For this endpoint, we only expect Lecturers to listen.
            # We could allow students if we wanted to broadcast generic events,
            # but for now we secure it for lecturers only.
            await websocket.close(code=1008, reason="Unauthorized user role")
            return

        # Check if the session exists
        session = crud.attendance_session.get(db, id=session_id)
        if not session:
            await websocket.close(code=1008, reason="Session not found")
            return

        # Verify the lecturer owns this session's course assignment
        course_assignment = crud.course_assignment.get(
            db, id=session.course_assignment_id
        )
        if not course_assignment or str(course_assignment.lecturer_id) != str(user_id):
            await websocket.close(code=1008, reason="Forbidden: Not your session")
            return

    except Exception as e:
        logger.error(f"WebSocket auth failed: {e}")
        await websocket.close(code=1008, reason="Authentication failed")
        return

    # Accept the connection
    await manager.connect(websocket, session_id)
    try:
        while True:
            # We just wait for disconnection. We don't expect the client to send messages here.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
