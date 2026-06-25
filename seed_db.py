import os
import sys

# Add the Backend directory to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app import crud, schemas
from app.models.department import Department
from app.models.course import Course
from app.models.academic_session import AcademicSession


def seed():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Recreating all tables...")
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    try:
        # Create Admin
        print("Seeding admin...")
        admin_in = schemas.UserCreate(
            email="admin@attendease.com",
            password="admin123",
            full_name="Super Admin",
            role="ADMIN",
        )
        admin = crud.user.create(db, obj_in=admin_in)

        # Create Department
        print("Seeding department...")
        dept = Department(name="Computer Science")
        db.add(dept)
        db.commit()
        db.refresh(dept)

        # Create Lecturer
        print("Seeding lecturer...")
        lecturer_in = schemas.LecturerCreate(
            email="lecturer@attendease.com",
            password="lecturer123",
            full_name="Dr. John Doe",
            staff_id="STAFF123",
            department_id=dept.id,
        )
        lecturer = crud.lecturer.create_with_user(db, obj_in=lecturer_in)

        # Create Student
        print("Seeding student...")
        student_in = schemas.StudentCreate(
            email="student@attendease.com",
            password="student123",
            full_name="Jane Smith",
            student_id="STU123",
            matric_number="CSC/2021/001",
            department_id=dept.id,
            level="300",
        )
        student = crud.student.create_with_user(db, obj_in=student_in)

        # Create Academic Session
        print("Seeding academic session...")
        session = AcademicSession(
            session_name="2025/2026",
            semester="First",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 30),
            is_active=True,
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        # Create Course
        print("Seeding course...")
        course = Course(
            course_code="CSC 301",
            title="Introduction to Database Systems",
            credit_units=3,
            department_id=dept.id,
        )
        db.add(course)
        db.commit()
        db.refresh(course)

        # Create Course Assignment
        print("Seeding course assignment...")
        assignment_in = schemas.CourseAssignmentCreate(
            course_id=course.id,
            lecturer_id=lecturer.user_id,
            academic_session_id=session.id,
        )
        crud.course_assignment.create(db, obj_in=assignment_in)

        print("Seeding complete!")
        print("\nCredentials:")
        print("Admin: admin@attendease.com / admin123")
        print("Lecturer: lecturer@attendease.com / lecturer123")
        print("Student: student@attendease.com / student123")

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
