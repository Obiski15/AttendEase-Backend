# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base
from app.models.user import User
from app.models.department import Department
from app.models.student import Student
from app.models.lecturer import Lecturer
from app.models.course import Course
from app.models.academic_session import AcademicSession
from app.models.course_assignment import CourseAssignment
from app.models.attendance_session import AttendanceSession
from app.models.attendance_record import AttendanceRecord
