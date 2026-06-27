from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AcademicSessionBase(BaseModel):
    session_name: Optional[str] = Field(default=None, description="Academic year or session name (e.g., 2026/2027).", example="2026/2027")
    semester: Optional[str] = Field(default=None, description="Semester (e.g., First, Second, Summer).", example="First")
    is_active: Optional[bool] = Field(default=False, description="Is this the currently active academic session?", example=True)
    start_date: Optional[date] = Field(default=None, description="Start date of the semester.", example="2026-09-01")
    end_date: Optional[date] = Field(default=None, description="End date of the semester.", example="2026-12-15")


class AcademicSessionCreate(BaseModel):
    session_name: str = Field(..., description="Academic year or session name (e.g., 2026/2027).", example="2026/2027")
    semester: str = Field(..., description="Semester (e.g., First, Second, Summer).", example="First")
    is_active: Optional[bool] = Field(default=False, description="Is this the currently active academic session?", example=True)
    start_date: date = Field(..., description="Start date of the semester.", example="2026-09-01")
    end_date: date = Field(..., description="End date of the semester.", example="2026-12-15")


class AcademicSessionUpdate(AcademicSessionBase):
    pass


class AcademicSession(AcademicSessionBase):
    id: UUID = Field(..., description="Unique ID of the academic session.", example="123e4567-e89b-12d3-a456-426614174007")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp.")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp.")

    model_config = {"from_attributes": True}
