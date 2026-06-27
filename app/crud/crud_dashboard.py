from datetime import datetime, timezone, timedelta
from uuid import UUID

from sqlalchemy import func, cast, Date
from sqlalchemy.orm import Session

from app.models.attendance_record import AttendanceRecord
from app.models.attendance_session import AttendanceSession
from app.models.course import Course
from app.models.course_assignment import CourseAssignment
from app.models.lecturer import Lecturer
from app.models.student import Student


def admin_stats(db: Session) -> dict:
    now = datetime.now(timezone.utc)
    result = {
        "total_students": db.query(func.count(Student.user_id)).scalar(),
        "total_lecturers": db.query(func.count(Lecturer.user_id)).scalar(),
        "total_courses": db.query(func.count(Course.id))
        .filter(Course.deleted_at.is_(None))
        .scalar(),
        "active_sessions": db.query(func.count(AttendanceSession.id))
        .filter(
            AttendanceSession.status == "ACTIVE",
            AttendanceSession.expires_at > now,
        )
        .scalar(),
    }
    
    seven_days_ago = now - timedelta(days=7)
    trend_rows = (
        db.query(
            cast(AttendanceRecord.check_in_time, Date).label("date_val"),
            func.count(AttendanceRecord.id).label("count")
        )
        .filter(AttendanceRecord.check_in_time >= seven_days_ago)
        .group_by("date_val")
        .order_by("date_val")
        .all()
    )
    result["weekly_attendance_trend"] = [
        {"date_str": str(r.date_val), "count": r.count} for r in trend_rows
    ]
    return result


def lecturer_dashboard(db: Session, *, lecturer_id: UUID, full_name: str) -> dict:
    now = datetime.now(timezone.utc)

    assigned_courses = (
        db.query(func.count(CourseAssignment.id))
        .filter(CourseAssignment.lecturer_id == lecturer_id)
        .scalar()
    )
    total_sessions = (
        db.query(func.count(AttendanceSession.id))
        .join(
            CourseAssignment,
            AttendanceSession.course_assignment_id == CourseAssignment.id,
        )
        .filter(CourseAssignment.lecturer_id == lecturer_id)
        .scalar()
    )
    active_rows = (
        db.query(
            AttendanceSession.id,
            Course.course_code,
            Course.title,
            AttendanceSession.session_code,
            AttendanceSession.expires_at,
            AttendanceSession.geofencing_enabled,
            AttendanceSession.radius_meters,
        )
        .join(
            CourseAssignment,
            AttendanceSession.course_assignment_id == CourseAssignment.id,
        )
        .join(Course, CourseAssignment.course_id == Course.id)
        .filter(
            CourseAssignment.lecturer_id == lecturer_id,
            AttendanceSession.status == "ACTIVE",
            AttendanceSession.expires_at > now,
        )
        .order_by(AttendanceSession.start_time.desc())
        .all()
    )
    course_rows = (
        db.query(
            CourseAssignment.id,
            Course.course_code,
            Course.title,
            Course.credit_units,
        )
        .join(Course, CourseAssignment.course_id == Course.id)
        .filter(CourseAssignment.lecturer_id == lecturer_id)
        .all()
    )
    
    distribution_rows = (
        db.query(
            Course.course_code.label("label"),
            func.count(AttendanceSession.id).label("count")
        )
        .join(
            CourseAssignment,
            AttendanceSession.course_assignment_id == CourseAssignment.id,
        )
        .join(Course, CourseAssignment.course_id == Course.id)
        .filter(CourseAssignment.lecturer_id == lecturer_id)
        .group_by(Course.course_code)
        .all()
    )

    return {
        "full_name": full_name,
        "assigned_courses": assigned_courses,
        "total_sessions": total_sessions,
        "active_sessions": [
            {
                "id": r.id,
                "course_code": r.course_code,
                "course_title": r.title,
                "session_code": r.session_code,
                "expires_at": r.expires_at,
                "geofencing_enabled": r.geofencing_enabled,
                "radius_meters": r.radius_meters,
            }
            for r in active_rows
        ],
        "courses": [
            {
                "course_assignment_id": r.id,
                "course_code": r.course_code,
                "course_title": r.title,
                "credit_units": r.credit_units,
            }
            for r in course_rows
        ],
        "course_distribution": [
            {
                "label": r.label,
                "count": r.count
            }
            for r in distribution_rows
        ]
    }


def student_dashboard(
    db: Session, *, student_id: UUID, full_name: str, recent_limit: int = 5
) -> dict:
    from app.models.student import Student
    
    student = db.query(Student).filter(Student.user_id == student_id).first()
    student_dept_id = student.department_id if student else None

    total_count = (
        db.query(func.count(AttendanceSession.id))
        .join(CourseAssignment, AttendanceSession.course_assignment_id == CourseAssignment.id)
        .join(Course, CourseAssignment.course_id == Course.id)
        .filter(Course.department_id == student_dept_id)
        .scalar()
    ) or 0

    present_count = (
        db.query(func.count(AttendanceRecord.id))
        .filter(
            AttendanceRecord.student_id == student_id,
            AttendanceRecord.status == "PRESENT",
        )
        .scalar()
    ) or 0
    
    percentage = round(present_count / total_count * 100, 1) if total_count else 0.0

    recent_rows = (
        db.query(
            Course.course_code,
            Course.title,
            AttendanceSession.session_date,
            AttendanceRecord.check_in_time,
            AttendanceRecord.status,
        )
        .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
        .join(
            CourseAssignment,
            AttendanceSession.course_assignment_id == CourseAssignment.id,
        )
        .join(Course, CourseAssignment.course_id == Course.id)
        .filter(AttendanceRecord.student_id == student_id)
        .order_by(AttendanceRecord.check_in_time.desc())
        .limit(recent_limit)
        .all()
    )

    return {
        "full_name": full_name,
        "attendance_percentage": percentage,
        "present_count": present_count,
        "total_count": total_count,
        "recent_attendance": [
            {
                "course_code": r.course_code,
                "course_title": r.title,
                "session_date": r.session_date,
                "check_in_time": r.check_in_time,
                "status": r.status,
            }
            for r in recent_rows
        ],
    }
