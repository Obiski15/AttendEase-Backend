from .token import Token, TokenRefresh, LoginPayload, LoginResponse
from .user import User, UserCreate, UserUpdate, PasswordUpdate, ProfileUpdate
from .department import Department, DepartmentCreate, DepartmentUpdate
from .student import Student, StudentCreate, StudentRegister, StudentUpdate
from .lecturer import Lecturer, LecturerCreate, LecturerUpdate
from .course import Course, CourseCreate, CourseUpdate
from .academic_session import AcademicSession, AcademicSessionCreate, AcademicSessionUpdate
from .course_assignment import CourseAssignment, CourseAssignmentCreate, CourseAssignmentUpdate
from .attendance_session import AttendanceSession, AttendanceSessionCreate, AttendanceSessionUpdate
from .attendance_record import (
    AttendanceRecord,
    AttendanceRecordCreate,
    AttendanceRecordUpdate,
    AttendanceCheckIn,
)
