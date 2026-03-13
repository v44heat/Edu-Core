from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime, date, time
from app.models.models import (
    RoleEnum, GenderEnum, AttendanceStatusEnum,
    SubmissionStatusEnum, FeeStatusEnum, AnnouncementTargetEnum
)


# ─── Auth Schemas ─────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class TokenRefresh(BaseModel):
    refresh_token: str


# ─── User Schemas ─────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    role: RoleEnum
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    role: RoleEnum
    phone: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Student Schemas ──────────────────────────────────────────────────────────

class StudentCreate(BaseModel):
    user_id: int
    student_id: str
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    address: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    parent_email: Optional[str] = None
    admission_date: Optional[date] = None
    class_id: Optional[int] = None


class StudentResponse(BaseModel):
    id: int
    student_id: str
    date_of_birth: Optional[date]
    gender: Optional[GenderEnum]
    address: Optional[str]
    parent_name: Optional[str]
    parent_phone: Optional[str]
    parent_email: Optional[str]
    admission_date: Optional[date]
    class_id: Optional[int]
    user: UserResponse

    class Config:
        from_attributes = True


# ─── Teacher Schemas ──────────────────────────────────────────────────────────

class TeacherCreate(BaseModel):
    user_id: int
    teacher_id: str
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    address: Optional[str] = None
    qualification: Optional[str] = None
    specialization: Optional[str] = None
    hire_date: Optional[date] = None
    salary: Optional[float] = None


class TeacherResponse(BaseModel):
    id: int
    teacher_id: str
    qualification: Optional[str]
    specialization: Optional[str]
    hire_date: Optional[date]
    user: UserResponse

    class Config:
        from_attributes = True


# ─── Class Schemas ────────────────────────────────────────────────────────────

class ClassCreate(BaseModel):
    name: str
    grade_level: str
    section: Optional[str] = None
    academic_year: str
    teacher_id: Optional[int] = None
    room_number: Optional[str] = None
    max_students: int = 40


class ClassResponse(BaseModel):
    id: int
    name: str
    grade_level: str
    section: Optional[str]
    academic_year: str
    room_number: Optional[str]
    max_students: int
    is_active: bool
    teacher_id: Optional[int]

    class Config:
        from_attributes = True


# ─── Subject Schemas ──────────────────────────────────────────────────────────

class SubjectCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    credit_hours: int = 1
    grade_level: Optional[str] = None


class SubjectResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str]
    credit_hours: int
    grade_level: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


# ─── Assignment Schemas ───────────────────────────────────────────────────────

class AssignmentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    subject_id: int
    class_id: int
    due_date: datetime
    max_score: float = 100.0


class AssignmentResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    subject_id: int
    class_id: int
    teacher_id: int
    due_date: datetime
    max_score: float
    file_url: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Submission Schemas ───────────────────────────────────────────────────────

class SubmissionCreate(BaseModel):
    assignment_id: int
    notes: Optional[str] = None


class SubmissionGrade(BaseModel):
    score: float
    feedback: Optional[str] = None


class SubmissionResponse(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    file_url: Optional[str]
    notes: Optional[str]
    status: SubmissionStatusEnum
    score: Optional[float]
    feedback: Optional[str]
    submitted_at: datetime
    graded_at: Optional[datetime]

    class Config:
        from_attributes = True


# ─── Grade Schemas ────────────────────────────────────────────────────────────

class GradeCreate(BaseModel):
    student_id: int
    subject_id: int
    class_id: int
    exam_name: str
    exam_type: Optional[str] = None
    score: float
    max_score: float = 100.0
    academic_year: Optional[str] = None
    term: Optional[str] = None
    remarks: Optional[str] = None


class GradeResponse(BaseModel):
    id: int
    student_id: int
    subject_id: int
    class_id: int
    exam_name: str
    exam_type: Optional[str]
    score: float
    max_score: float
    grade_letter: Optional[str]
    academic_year: Optional[str]
    term: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Attendance Schemas ───────────────────────────────────────────────────────

class AttendanceCreate(BaseModel):
    student_id: int
    class_id: int
    subject_id: Optional[int] = None
    date: date
    status: AttendanceStatusEnum
    notes: Optional[str] = None


class AttendanceResponse(BaseModel):
    id: int
    student_id: int
    class_id: int
    date: date
    status: AttendanceStatusEnum
    notes: Optional[str]

    class Config:
        from_attributes = True


# ─── Announcement Schemas ─────────────────────────────────────────────────────

class AnnouncementCreate(BaseModel):
    title: str
    content: str
    target_audience: AnnouncementTargetEnum = AnnouncementTargetEnum.all
    target_class_id: Optional[int] = None
    is_pinned: bool = False
    expires_at: Optional[datetime] = None


class AnnouncementResponse(BaseModel):
    id: int
    title: str
    content: str
    target_audience: AnnouncementTargetEnum
    target_class_id: Optional[int]
    is_pinned: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Fee Schemas ──────────────────────────────────────────────────────────────

class FeeCreate(BaseModel):
    student_id: int
    fee_type: str
    amount: float
    due_date: date
    academic_year: Optional[str] = None
    term: Optional[str] = None
    notes: Optional[str] = None


class FeePayment(BaseModel):
    paid_amount: float
    transaction_ref: Optional[str] = None


class FeeResponse(BaseModel):
    id: int
    student_id: int
    fee_type: str
    amount: float
    paid_amount: float
    due_date: date
    payment_date: Optional[date]
    status: FeeStatusEnum
    academic_year: Optional[str]
    term: Optional[str]
    transaction_ref: Optional[str]

    class Config:
        from_attributes = True


# ─── Timetable Schemas ────────────────────────────────────────────────────────

class TimetableSlotCreate(BaseModel):
    class_id: int
    subject_id: int
    teacher_id: Optional[int] = None
    day_of_week: int
    start_time: time
    end_time: time
    room: Optional[str] = None
    academic_year: Optional[str] = None


class TimetableSlotResponse(BaseModel):
    id: int
    class_id: int
    subject_id: int
    teacher_id: Optional[int]
    day_of_week: int
    start_time: time
    end_time: time
    room: Optional[str]

    class Config:
        from_attributes = True


# ─── Notification Schemas ─────────────────────────────────────────────────────

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    type: Optional[str]
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Dashboard Schemas ────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_students: int
    total_teachers: int
    total_classes: int
    total_subjects: int
    recent_announcements: List[AnnouncementResponse]
    attendance_rate: float


class StudentDashboard(BaseModel):
    student: StudentResponse
    enrolled_subjects: List[SubjectResponse]
    upcoming_assignments: List[AssignmentResponse]
    recent_grades: List[GradeResponse]
    attendance_summary: dict
    fee_summary: dict
    announcements: List[AnnouncementResponse]
    unread_notifications: int
