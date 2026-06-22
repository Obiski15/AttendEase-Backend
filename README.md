# AttendEase Backend

Backend API for the AttendEase attendance management system, built with **FastAPI** and **PostgreSQL**.

## Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Database:** PostgreSQL 16
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Validation:** Pydantic v2

## Project Structure

```
app/
├── main.py                  # FastAPI application entry point
├── core/
│   └── config.py            # Settings and environment variables
├── db/
│   ├── base.py              # Imports all models for Alembic discovery
│   ├── base_class.py        # SQLAlchemy declarative Base class
│   └── session.py           # Database engine and session factory
├── models/                  # SQLAlchemy ORM models (one file per entity)
│   ├── item.py
│   └── user.py
├── schemas/                 # Pydantic request/response schemas
│   ├── item.py
│   └── user.py
├── crud/                    # Database CRUD operations
│   ├── base.py              # Generic CRUDBase class
│   ├── crud_item.py
│   └── crud_user.py
└── api/
    ├── deps.py              # Shared dependencies (e.g. get_db)
    └── v1/
        ├── api.py           # v1 router aggregator
        └── endpoints/       # Route handlers (one file per entity)
            ├── items.py
            └── users.py
```

## Getting Started

### Prerequisites

- Python 3.10+
- Docker (for PostgreSQL)
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AttendEase/Backend
```

### 2. Create and Activate Virtual Environment

```bash
# Create
python -m venv venv

# Activate (Linux/macOS/Git Bash)
source venv/Scripts/activate   # Windows Git Bash
source venv/bin/activate       # Linux/macOS

# Activate (PowerShell)
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```env
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### 5. Start PostgreSQL

```bash
docker-compose up -d
```

### 6. Run the Development Server

```bash
uvicorn app.main:app --reload
```

The API will be available at:

| URL                          | Description              |
|------------------------------|--------------------------|
| http://127.0.0.1:8000        | Root health check        |
| http://127.0.0.1:8000/docs   | Swagger UI (interactive) |
| http://127.0.0.1:8000/redoc  | ReDoc (read-only docs)   |

## Adding a New Entity

Follow these steps to add a new entity (e.g. `Attendance`):

### Step 1 — Model

Create `app/models/attendance.py`:

```python
from sqlalchemy import Column, Integer, String, DateTime

from app.db.base_class import Base


class Attendance(Base):
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
```

Then register it in `app/models/__init__.py`:

```python
from .attendance import Attendance
```

And in `app/db/base.py`:

```python
from app.models.attendance import Attendance
```

### Step 2 — Schema

Create `app/schemas/attendance.py`:

```python
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AttendanceBase(BaseModel):
    student_id: int
    timestamp: datetime


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(AttendanceBase):
    student_id: Optional[int] = None
    timestamp: Optional[datetime] = None


class Attendance(AttendanceBase):
    id: int

    model_config = {"from_attributes": True}
```

Then register it in `app/schemas/__init__.py`:

```python
from .attendance import Attendance, AttendanceCreate, AttendanceUpdate
```

### Step 3 — CRUD

Create `app/crud/crud_attendance.py`:

```python
from app.crud.base import CRUDBase
from app.models.attendance import Attendance
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate


class CRUDAttendance(CRUDBase[Attendance, AttendanceCreate, AttendanceUpdate]):
    pass


attendance = CRUDAttendance(Attendance)
```

Then register it in `app/crud/__init__.py`:

```python
from .crud_attendance import attendance
```

### Step 4 — Endpoint

Create `app/api/v1/endpoints/attendance.py`:

```python
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Attendance])
def read_attendances(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Retrieve attendance records."""
    return crud.attendance.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=schemas.Attendance)
def create_attendance(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.AttendanceCreate,
) -> Any:
    """Create new attendance record."""
    return crud.attendance.create(db=db, obj_in=obj_in)
```

### Step 5 — Register the Router

In `app/api/v1/api.py`:

```python
from app.api.v1.endpoints import attendance

api_router.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
```

### Step 6 — Update Swagger Tags (optional)

In `app/main.py`, add the tag to `openapi_tags`:

```python
{"name": "attendance", "description": "Attendance tracking operations."},
```

## Code Style

- Follow **PEP 8** formatting
- Use **2 blank lines** before top-level classes and functions
- Comments should explain **why**, not **what**
- Run `flake8 app/` before committing

## Useful Commands

```bash
# Start dev server
uvicorn app.main:app --reload

# Start database
docker-compose up -d

# Stop database
docker-compose down

# Lint code
flake8 app/

# Freeze dependencies
pip freeze > requirements.txt
```
