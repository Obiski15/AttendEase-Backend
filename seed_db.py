import os
import sys
import random
import time

# Add the Backend directory to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date, datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app import crud, schemas
from app.models.department import Department
from app.models.course import Course
from app.models.academic_session import AcademicSession
from app.models.course_assignment import CourseAssignment
from app.models.attendance_session import AttendanceSession
from app.models.attendance_record import AttendanceRecord

# Dummy Data Pools
FIRST_NAMES = ["John", "Jane", "Michael", "Sarah", "David", "Emma", "Daniel", "Olivia", "James", "Sophia", "Matthew", "Ava", "Joseph", "Isabella", "Samuel", "Mia"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez"]
LEVELS = ["100", "200", "300", "400", "500"]

def get_random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def seed():
    start_time_benchmark = time.time()
    
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Recreating all tables...")
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    try:
        # 1. Create Admin
        print("Seeding admin...")
        admin_in = schemas.UserCreate(
            email="admin@attendease.com",
            password="admin123",
            full_name="Super Admin",
            role="ADMIN",
        )
        crud.user.create(db, obj_in=admin_in)

        # 2. Create Departments
        print("Seeding departments...")
        dept_names = ["Computer Science", "Mathematics", "Electrical Engineering"]
        departments = []
        for name in dept_names:
            dept = Department(name=name)
            db.add(dept)
            departments.append(dept)
        db.commit()
        for d in departments:
            db.refresh(d)

        # 3. Create Lecturers
        print("Seeding lecturers...")
        lecturers = []
        for i in range(1, 6):
            dept = random.choice(departments)
            lecturer_in = schemas.LecturerCreate(
                email=f"lecturer{i}@attendease.com",
                password="lecturer123",
                full_name=f"Dr. {get_random_name()}",
                staff_id=f"STAFF{1000 + i}",
                department_id=dept.id,
            )
            lecturer = crud.lecturer.create_with_user(db, obj_in=lecturer_in)
            lecturers.append(lecturer)

        # 4. Create Students
        print("Seeding students...")
        students = []
        for i in range(1, 21):
            dept = random.choice(departments)
            level = random.choice(LEVELS)
            dept_code = dept.name[:3].upper()
            
            student_in = schemas.StudentCreate(
                email=f"student{i}@attendease.com",
                password="student123",
                full_name=get_random_name(),
                student_id=f"STU{2000 + i}",
                matric_number=f"{dept_code}/2021/{i:03d}",
                department_id=dept.id,
                level=level,
            )
            student = crud.student.create_with_user(db, obj_in=student_in)
            students.append(student)

        # 5. Create Academic Session
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

        # 6. Create Courses
        print("Seeding courses...")
        course_data = [
            ("CSC 301", "Database Systems", 3, departments[0].id),
            ("CSC 302", "Software Engineering", 3, departments[0].id),
            ("CSC 401", "Artificial Intelligence", 4, departments[0].id),
            ("MAT 101", "Calculus I", 3, departments[1].id),
            ("MAT 202", "Linear Algebra", 2, departments[1].id),
            ("MAT 305", "Differential Equations", 3, departments[1].id),
            ("EEE 201", "Circuit Theory", 3, departments[2].id),
            ("EEE 302", "Electromagnetics", 4, departments[2].id),
            ("EEE 405", "Digital Signal Processing", 3, departments[2].id),
        ]
        
        courses = []
        for code, title, units, dept_id in course_data:
            course = Course(course_code=code, title=title, credit_units=units, department_id=dept_id)
            db.add(course)
            courses.append(course)
        db.commit()
        for c in courses:
            db.refresh(c)

        # 7. Create Course Assignments
        print("Seeding course assignments...")
        assignments = []
        for course in courses:
            eligible_lecturers = [l for l in lecturers if l.department_id == course.department_id]
            lecturer = random.choice(eligible_lecturers) if eligible_lecturers else random.choice(lecturers)
            
            assignment = CourseAssignment(
                course_id=course.id,
                lecturer_id=lecturer.user_id,
                academic_session_id=session.id,
            )
            db.add(assignment)
            assignments.append(assignment)
        db.commit()
        for a in assignments:
            db.refresh(a)

        # 8. Create Attendance Sessions and Records for visual graphs   
        print("Seeding robust historical attendance data (Bulk inserting for speed)...")    
        now = datetime.now(timezone.utc)
        
        session_counter = 1
        all_attendance_records = []

        for assignment in assignments:
            num_sessions = random.randint(5, 10)
            
            course_dept_id = next(c.department_id for c in courses if c.id == assignment.course_id)
            enrolled_students = [s for s in students if s.department_id == course_dept_id]

            for _ in range(num_sessions):
                days_ago = random.randint(0, 30)
                hour_of_day = random.randint(8, 16) 
                
                start_time = (now - timedelta(days=days_ago)).replace(hour=hour_of_day, minute=0, second=0, microsecond=0)
                end_time = start_time + timedelta(hours=random.choice([1, 2]))

                # Create Session
                att_session = AttendanceSession(
                    course_assignment_id=assignment.id,
                    session_date=start_time.date(),
                    start_time=start_time,
                    expires_at=end_time,
                    session_code=f"CODE{session_counter:04d}",
                    status="COMPLETED" if start_time < now else "ACTIVE",
                    geofencing_enabled=random.choice([True, False])
                )
                db.add(att_session)
                db.flush()
                session_counter += 1

                # Create Records for enrolled students
                for student in enrolled_students:
                    status = random.choices(
                        population=["PRESENT", "ABSENT"], 
                        weights=[0.85, 0.15],
                        k=1
                    )[0]

                    if status == "PRESENT":
                        check_in_time = start_time + timedelta(minutes=random.randint(0, 15))
                    else:
                        check_in_time = end_time 

                    record = AttendanceRecord(
                        session_id=att_session.id,
                        student_id=student.user_id,
                        check_in_time=check_in_time,
                        status=status
                    )
                    all_attendance_records.append(record)

        # Bulk insert all records
        print(f"Pushing {len(all_attendance_records)} attendance records to the database...")
        db.add_all(all_attendance_records)
        db.commit()

        elapsed_time = round(time.time() - start_time_benchmark, 2)
        print(f"Seeding complete in {elapsed_time} seconds!")
        
        print("\n--- Test Credentials ---")
        print("Admin   : admin@attendease.com / admin123")
        print("Lecturer: lecturer1@attendease.com / lecturer123 (up to lecturer5@...)")     
        print("Student : student1@attendease.com / student123 (up to student20@...)")        
        print("------------------------\n")

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed()