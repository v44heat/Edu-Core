from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Float,
    Text, ForeignKey, Enum, Date, Time, BigInteger, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


# ─── Enums ────────────────────────────────────────────────────────────────────

class RoleEnum(str, enum.Enum):
    super_admin = "super_admin"
    admin = "admin"
    teacher = "teacher"
    student = "student"


class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"


class AttendanceStatusEnum(str, enum.Enum):
    present = "present"
    absent = "absent"
    late = "late"
    excused = "excused"


class SubmissionStatusEnum(str, enum.Enum):
    submitted = "submitted"
    graded = "graded"
    late = "late"
    missing = "missing"


class FeeStatusEnum(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    overdue = "overdue"
    partial = "partial"


class AnnouncementTargetEnum(str, enum.Enum):
    all = "all"
    students = "students"
    teachers = "teachers"
    class_specific = "class_specific"


# ─── Models ───────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.student)
    phone = Column(String(20))
    avatar_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    student_profile = relationship("Student", back_populates="user", uselist=False)
    teacher_profile = relationship("Teacher", back_populates="user", uselist=False)
    activity_logs = relationship("ActivityLog", back_populates="user")
    notifications = relationship("Notification", back_populates="user")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    student_id = Column(String(20), unique=True, index=True, nullable=False)
    date_of_birth = Column(Date)
    gender = Column(Enum(GenderEnum))
    address = Column(Text)
    parent_name = Column(String(255))
    parent_phone = Column(String(20))
    parent_email = Column(String(255))
    admission_date = Column(Date)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="student_profile")
    current_class = relationship("Class", back_populates="students")
    enrollments = relationship("Enrollment", back_populates="student")
    submissions = relationship("Submission", back_populates="student")
    attendances = relationship("Attendance", back_populates="student")
    grades = relationship("Grade", back_populates="student")
    fees = relationship("Fee", back_populates="student")


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    teacher_id = Column(String(20), unique=True, index=True, nullable=False)
    date_of_birth = Column(Date)
    gender = Column(Enum(GenderEnum))
    address = Column(Text)
    qualification = Column(String(255))
    specialization = Column(String(255))
    hire_date = Column(Date)
    salary = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="teacher_profile")
    classes = relationship("Class", back_populates="class_teacher")
    subject_assignments = relationship("SubjectAssignment", back_populates="teacher")
    assignments = relationship("Assignment", back_populates="teacher")
    attendance_records = relationship("Attendance", back_populates="recorded_by")
    announcements = relationship("Announcement", back_populates="created_by_teacher")


class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    grade_level = Column(String(20), nullable=False)
    section = Column(String(10))
    academic_year = Column(String(20), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="SET NULL"))
    room_number = Column(String(20))
    max_students = Column(Integer, default=40)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    class_teacher = relationship("Teacher", back_populates="classes")
    students = relationship("Student", back_populates="current_class")
    enrollments = relationship("Enrollment", back_populates="class_")
    subject_assignments = relationship("SubjectAssignment", back_populates="class_")
    timetable_slots = relationship("TimetableSlot", back_populates="class_")
    announcements = relationship("Announcement", back_populates="target_class")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text)
    credit_hours = Column(Integer, default=1)
    grade_level = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    subject_assignments = relationship("SubjectAssignment", back_populates="subject")
    assignments = relationship("Assignment", back_populates="subject")
    grades = relationship("Grade", back_populates="subject")
    timetable_slots = relationship("TimetableSlot", back_populates="subject")


class SubjectAssignment(Base):
    """Maps teachers to subjects for specific classes"""
    __tablename__ = "subject_assignments"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"))
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"))
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"))
    academic_year = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    teacher = relationship("Teacher", back_populates="subject_assignments")
    subject = relationship("Subject", back_populates="subject_assignments")
    class_ = relationship("Class", back_populates="subject_assignments")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"))
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"))
    academic_year = Column(String(20), nullable=False)
    enrollment_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    student = relationship("Student", back_populates="enrollments")
    class_ = relationship("Class", back_populates="enrollments")
    subject = relationship("Subject")


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"))
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"))
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"))
    due_date = Column(DateTime(timezone=True), nullable=False)
    max_score = Column(Float, default=100.0)
    file_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    teacher = relationship("Teacher", back_populates="assignments")
    subject = relationship("Subject", back_populates="assignments")
    class_ = relationship("Class")
    submissions = relationship("Submission", back_populates="assignment")


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"))
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    file_url = Column(String(500))
    notes = Column(Text)
    status = Column(Enum(SubmissionStatusEnum), default=SubmissionStatusEnum.submitted)
    score = Column(Float)
    feedback = Column(Text)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    graded_at = Column(DateTime(timezone=True))

    # Relationships
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("Student", back_populates="submissions")


class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"))
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"))
    exam_name = Column(String(100), nullable=False)
    exam_type = Column(String(50))  # midterm, final, quiz, etc.
    score = Column(Float, nullable=False)
    max_score = Column(Float, default=100.0)
    grade_letter = Column(String(5))
    academic_year = Column(String(20))
    term = Column(String(20))
    remarks = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    student = relationship("Student", back_populates="grades")
    subject = relationship("Subject", back_populates="grades")
    class_ = relationship("Class")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"))
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="SET NULL"))
    date = Column(Date, nullable=False)
    status = Column(Enum(AttendanceStatusEnum), nullable=False)
    recorded_by_id = Column(Integer, ForeignKey("teachers.id", ondelete="SET NULL"))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    student = relationship("Student", back_populates="attendances")
    class_ = relationship("Class")
    subject = relationship("Subject")
    recorded_by = relationship("Teacher", back_populates="attendance_records")


class TimetableSlot(Base):
    __tablename__ = "timetable_slots"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"))
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"))
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="SET NULL"))
    day_of_week = Column(Integer, nullable=False)  # 0=Mon, 6=Sun
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    room = Column(String(50))
    academic_year = Column(String(20))

    # Relationships
    class_ = relationship("Class", back_populates="timetable_slots")
    subject = relationship("Subject", back_populates="timetable_slots")
    teacher = relationship("Teacher")


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    target_audience = Column(Enum(AnnouncementTargetEnum), default=AnnouncementTargetEnum.all)
    target_class_id = Column(Integer, ForeignKey("classes.id", ondelete="SET NULL"))
    created_by_teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="SET NULL"))
    created_by_admin_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    is_pinned = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    target_class = relationship("Class", back_populates="announcements")
    created_by_teacher = relationship("Teacher", back_populates="announcements")


class Fee(Base):
    __tablename__ = "fees"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    fee_type = Column(String(100), nullable=False)  # tuition, exam, library, etc.
    amount = Column(Float, nullable=False)
    paid_amount = Column(Float, default=0.0)
    due_date = Column(Date, nullable=False)
    payment_date = Column(Date)
    status = Column(Enum(FeeStatusEnum), default=FeeStatusEnum.pending)
    academic_year = Column(String(20))
    term = Column(String(20))
    transaction_ref = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    student = relationship("Student", back_populates="fees")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50))  # assignment, grade, announcement, fee, etc.
    is_read = Column(Boolean, default=False)
    related_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="notifications")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String(100), nullable=False)
    resource = Column(String(100))
    resource_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="activity_logs")
