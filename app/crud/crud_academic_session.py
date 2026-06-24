from typing import Any, Dict, Union
from sqlalchemy.orm import Session


from app.crud.base import CRUDBase
from app.models.academic_session import AcademicSession
from app.schemas.academic_session import AcademicSessionCreate, AcademicSessionUpdate


class CRUDAcademicSession(
    CRUDBase[AcademicSession, AcademicSessionCreate, AcademicSessionUpdate]
):
    def create(self, db: Session, *, obj_in: AcademicSessionCreate) -> AcademicSession:
        if obj_in.start_date > obj_in.end_date:
            raise ValueError("Start date must be before or equal to end date.")

        if obj_in.is_active:
            # Overlap check
            active_session = db.query(AcademicSession).filter(
                AcademicSession.is_active.is_(True)
            ).first()
            if active_session:
                if (active_session.start_date and active_session.end_date and
                        active_session.start_date <= obj_in.end_date and
                        obj_in.start_date <= active_session.end_date):
                    raise ValueError(
                        "Cannot activate academic session. "
                        "It overlaps with the date range of the currently active session."
                    )
            db.query(AcademicSession).update({AcademicSession.is_active: False})
        return super().create(db, obj_in=obj_in)

    def update(
        self,
        db: Session,
        *,
        db_obj: AcademicSession,
        obj_in: Union[AcademicSessionUpdate, Dict[str, Any]]
    ) -> AcademicSession:
        # Extract new values or fall back to current values
        if isinstance(obj_in, dict):
            start_date = obj_in.get("start_date", db_obj.start_date)
            end_date = obj_in.get("end_date", db_obj.end_date)
            is_active = obj_in.get("is_active", False)
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            start_date = update_data.get("start_date", db_obj.start_date)
            end_date = update_data.get("end_date", db_obj.end_date)
            is_active = update_data.get("is_active", False)

        if start_date and end_date:
            if start_date > end_date:
                raise ValueError("Start date must be before or equal to end date.")

        if is_active:
            # Overlap check
            active_session = db.query(AcademicSession).filter(
                AcademicSession.is_active.is_(True),
                AcademicSession.id != db_obj.id
            ).first()
            if active_session:
                if (active_session.start_date and active_session.end_date and
                        active_session.start_date <= end_date and
                        start_date <= active_session.end_date):
                    raise ValueError(
                        "Cannot activate academic session. "
                        "It overlaps with the date range of the currently active session."
                    )
            db.query(AcademicSession).update({AcademicSession.is_active: False})

        return super().update(db, db_obj=db_obj, obj_in=obj_in)

    def activate(self, db: Session, *, db_obj: AcademicSession) -> AcademicSession:
        """Mark this session active and deactivate all others (only one active)."""
        # Overlap check
        active_session = db.query(AcademicSession).filter(
            AcademicSession.is_active.is_(True),
            AcademicSession.id != db_obj.id
        ).first()
        if active_session:
            if (active_session.start_date and active_session.end_date and
                    db_obj.start_date and db_obj.end_date and
                    active_session.start_date <= db_obj.end_date and
                    db_obj.start_date <= active_session.end_date):
                raise ValueError(
                    "Cannot activate academic session. "
                    "It overlaps with the date range of the currently active session."
                )

        db.query(AcademicSession).update({AcademicSession.is_active: False})
        db_obj.is_active = True
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


academic_session = CRUDAcademicSession(AcademicSession)
