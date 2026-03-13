from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date
from app.core.database import get_db
from app.models.models import (
    Student, Teacher, Class, Subject, SubjectAssignment,
    Enrollment, User, RoleEnum
)
from app.schemas.schemas import (
    StudentCreate, StudentResponse, TeacherCreate, TeacherResponse,
    ClassCreate, ClassResponse, SubjectCreate, SubjectResponse
)
from app.api.deps import get_current_user, require_admin, require_teacher

# ─── Students ─────────────────────────────────────────────────────────────────
students_router = APIRouter(prefix="/students", tags=["Students"])

@students_router.get("/", response_model=List[StudentResponse])
def list_students(
    skip: int = 0, limit: int = 50,
    class_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_teacher),
):
    query = db.query(Student).options(joinedload(Student.user))
    if class_id:
        query = query.filter(Student.class_id == class_id)
    if search:
        query = query.join(User).filter(
            (User.full_name.ilike(f"%{search}%")) | (Student.student_id.ilike(f"%{search}%"))
        )
    return query.offset(skip).limit(limit).all()


@students_router.post("/", response_model=StudentResponse, status_code=201)
def create_student(data: StudentCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    if db.query(Student).filter(Student.student_id == data.student_id).first():
        raise HTTPException(status_code=400, detail="Student ID already exists")
    student = Student(**data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@students_router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    student = db.query(Student).options(joinedload(Student.user)).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    # Students can only view their own profile
    if current_user.role == RoleEnum.student and student.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return student


@students_router.get("/{student_id}/dashboard")
def student_dashboard(student_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.models.models import Assignment, Grade, Attendance, Fee, Announcement, Notification
    from sqlalchemy import func
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Attendance stats
    att_total = db.query(Attendance).filter(Attendance.student_id == student_id).count()
    att_present = db.query(Attendance).filter(
        Attendance.student_id == student_id, Attendance.status == "present"
    ).count()

    # Fee summary
    fees = db.query(Fee).filter(Fee.student_id == student_id).all()
    total_fees = sum(f.amount for f in fees)
    paid_fees = sum(f.paid_amount for f in fees)

    # Recent grades
    grades = db.query(Grade).filter(Grade.student_id == student_id).order_by(Grade.created_at.desc()).limit(5).all()

    # Unread notifications
    unread = db.query(Notification).filter(
        Notification.user_id == current_user.id, Notification.is_read == False
    ).count()

    return {
        "attendance_rate": round((att_present / att_total * 100) if att_total > 0 else 0, 1),
        "attendance_total": att_total,
        "attendance_present": att_present,
        "fee_total": total_fees,
        "fee_paid": paid_fees,
        "fee_balance": total_fees - paid_fees,
        "recent_grades": [{"exam": g.exam_name, "score": g.score, "max": g.max_score, "letter": g.grade_letter} for g in grades],
        "unread_notifications": unread,
    }


# ─── Teachers ─────────────────────────────────────────────────────────────────
teachers_router = APIRouter(prefix="/teachers", tags=["Teachers"])

@teachers_router.get("/", response_model=List[TeacherResponse])
def list_teachers(
    skip: int = 0, limit: int = 50, search: Optional[str] = None,
    db: Session = Depends(get_db), _: User = Depends(require_admin),
):
    query = db.query(Teacher).options(joinedload(Teacher.user))
    if search:
        query = query.join(User).filter(User.full_name.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()


@teachers_router.post("/", response_model=TeacherResponse, status_code=201)
def create_teacher(data: TeacherCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    if db.query(Teacher).filter(Teacher.teacher_id == data.teacher_id).first():
        raise HTTPException(status_code=400, detail="Teacher ID already exists")
    teacher = Teacher(**data.model_dump())
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


@teachers_router.get("/{teacher_id}", response_model=TeacherResponse)
def get_teacher(teacher_id: int, db: Session = Depends(get_db), _: User = Depends(require_teacher)):
    teacher = db.query(Teacher).options(joinedload(Teacher.user)).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher


# ─── Classes ──────────────────────────────────────────────────────────────────
classes_router = APIRouter(prefix="/classes", tags=["Classes"])

@classes_router.get("/", response_model=List[ClassResponse])
def list_classes(
    skip: int = 0, limit: int = 50, academic_year: Optional[str] = None,
    db: Session = Depends(get_db), _: User = Depends(get_current_user),
):
    query = db.query(Class).filter(Class.is_active == True)
    if academic_year:
        query = query.filter(Class.academic_year == academic_year)
    return query.offset(skip).limit(limit).all()


@classes_router.post("/", response_model=ClassResponse, status_code=201)
def create_class(data: ClassCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    class_ = Class(**data.model_dump())
    db.add(class_)
    db.commit()
    db.refresh(class_)
    return class_


@classes_router.get("/{class_id}/students", response_model=List[StudentResponse])
def get_class_students(class_id: int, db: Session = Depends(get_db), _: User = Depends(require_teacher)):
    return db.query(Student).options(joinedload(Student.user)).filter(Student.class_id == class_id).all()


# ─── Subjects ─────────────────────────────────────────────────────────────────
subjects_router = APIRouter(prefix="/subjects", tags=["Subjects"])

@subjects_router.get("/", response_model=List[SubjectResponse])
def list_subjects(
    skip: int = 0, limit: int = 50, grade_level: Optional[str] = None,
    db: Session = Depends(get_db), _: User = Depends(get_current_user),
):
    query = db.query(Subject).filter(Subject.is_active == True)
    if grade_level:
        query = query.filter(Subject.grade_level == grade_level)
    return query.offset(skip).limit(limit).all()


@subjects_router.post("/", response_model=SubjectResponse, status_code=201)
def create_subject(data: SubjectCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    if db.query(Subject).filter(Subject.code == data.code).first():
        raise HTTPException(status_code=400, detail="Subject code already exists")
    subject = Subject(**data.model_dump())
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject
