from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.academic_session import AcademicSession
from app.schemas.academic_session import AcademicSessionCreate, AcademicSessionUpdate


class CRUDAcademicSession(
    CRUDBase[AcademicSession, AcademicSessionCreate, AcademicSessionUpdate]
):
    def activate(self, db: Session, *, db_obj: AcademicSession) -> AcademicSession:
        """Mark this session active and deactivate all others (only one active)."""
        db.query(AcademicSession).update({AcademicSession.is_active: False})
        db_obj.is_active = True
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


academic_session = CRUDAcademicSession(AcademicSession)
