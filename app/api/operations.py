import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, datetime
from app.core.database import get_db
from app.core.config import settings
from app.models.models import (
    Assignment, Submission, Grade, Attendance, Announcement, Fee,
    Notification, TimetableSlot, User, Student, Teacher, RoleEnum,
    SubmissionStatusEnum, FeeStatusEnum, AttendanceStatusEnum
)
from app.schemas.schemas import (
    AssignmentCreate, AssignmentResponse, SubmissionCreate, SubmissionGrade,
    SubmissionResponse, GradeCreate, GradeResponse, AttendanceCreate,
    AttendanceResponse, AnnouncementCreate, AnnouncementResponse,
    FeeCreate, FeePayment, FeeResponse, TimetableSlotCreate, TimetableSlotResponse,
    NotificationResponse
)
from app.api.deps import get_current_user, require_admin, require_teacher

GRADE_THRESHOLDS = [
    (90, "A+"), (80, "A"), (75, "B+"), (70, "B"),
    (65, "C+"), (60, "C"), (50, "D"), (0, "F")
]

def calculate_grade_letter(score: float, max_score: float) -> str:
    percentage = (score / max_score) * 100
    for threshold, letter in GRADE_THRESHOLDS:
        if percentage >= threshold:
            return letter
    return "F"


# ─── Assignments ──────────────────────────────────────────────────────────────
assignments_router = APIRouter(prefix="/assignments", tags=["Assignments"])

@assignments_router.get("/", response_model=List[AssignmentResponse])
def list_assignments(
    class_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Assignment).filter(Assignment.is_active == True)
    if class_id:
        query = query.filter(Assignment.class_id == class_id)
    if subject_id:
        query = query.filter(Assignment.subject_id == subject_id)
    if current_user.role == RoleEnum.teacher and current_user.teacher_profile:
        query = query.filter(Assignment.teacher_id == current_user.teacher_profile.id)
    return query.order_by(Assignment.due_date.asc()).offset(skip).limit(limit).all()


@assignments_router.post("/", response_model=AssignmentResponse, status_code=201)
def create_assignment(
    data: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher),
):
    teacher = current_user.teacher_profile
    if not teacher and current_user.role != RoleEnum.admin:
        raise HTTPException(status_code=400, detail="Teacher profile required")
    teacher_id = teacher.id if teacher else None
    assignment = Assignment(**data.model_dump(), teacher_id=teacher_id)
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@assignments_router.post("/{assignment_id}/upload")
async def upload_assignment_file(
    assignment_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher),
):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    os.makedirs(f"{settings.UPLOAD_DIR}/assignments", exist_ok=True)
    filename = f"{assignment_id}_{file.filename}"
    filepath = f"{settings.UPLOAD_DIR}/assignments/{filename}"

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    assignment.file_url = filepath
    db.commit()
    return {"file_url": filepath}


# ─── Submissions ──────────────────────────────────────────────────────────────
submissions_router = APIRouter(prefix="/submissions", tags=["Submissions"])

@submissions_router.post("/", response_model=SubmissionResponse, status_code=201)
async def submit_assignment(
    assignment_id: int,
    notes: Optional[str] = None,
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != RoleEnum.student or not current_user.student_profile:
        raise HTTPException(status_code=403, detail="Student access required")

    student = current_user.student_profile
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    existing = db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.student_id == student.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already submitted")

    file_url = None
    if file:
        os.makedirs(f"{settings.UPLOAD_DIR}/submissions", exist_ok=True)
        filename = f"{assignment_id}_{student.id}_{file.filename}"
        filepath = f"{settings.UPLOAD_DIR}/submissions/{filename}"
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_url = filepath

    is_late = datetime.utcnow() > assignment.due_date
    submission = Submission(
        assignment_id=assignment_id,
        student_id=student.id,
        notes=notes,
        file_url=file_url,
        status=SubmissionStatusEnum.late if is_late else SubmissionStatusEnum.submitted,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


@submissions_router.put("/{submission_id}/grade", response_model=SubmissionResponse)
def grade_submission(
    submission_id: int,
    grade_data: SubmissionGrade,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher),
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    submission.score = grade_data.score
    submission.feedback = grade_data.feedback
    submission.status = SubmissionStatusEnum.graded
    submission.graded_at = datetime.utcnow()

    # Create notification
    notif = Notification(
        user_id=submission.student.user_id,
        title="Assignment Graded",
        message=f"Your submission has been graded: {grade_data.score}/{submission.assignment.max_score}",
        type="grade",
        related_id=submission_id,
    )
    db.add(notif)
    db.commit()
    db.refresh(submission)
    return submission


# ─── Grades ───────────────────────────────────────────────────────────────────
grades_router = APIRouter(prefix="/grades", tags=["Grades"])

@grades_router.get("/", response_model=List[GradeResponse])
def list_grades(
    student_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Grade)
    if current_user.role == RoleEnum.student and current_user.student_profile:
        query = query.filter(Grade.student_id == current_user.student_profile.id)
    elif student_id:
        query = query.filter(Grade.student_id == student_id)
    if subject_id:
        query = query.filter(Grade.subject_id == subject_id)
    if class_id:
        query = query.filter(Grade.class_id == class_id)
    return query.order_by(Grade.created_at.desc()).all()


@grades_router.post("/", response_model=GradeResponse, status_code=201)
def create_grade(
    data: GradeCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_teacher),
):
    grade_letter = calculate_grade_letter(data.score, data.max_score)
    grade = Grade(**data.model_dump(), grade_letter=grade_letter)
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade


@grades_router.get("/analytics/{class_id}")
def grade_analytics(class_id: int, subject_id: Optional[int] = None, db: Session = Depends(get_db), _: User = Depends(require_teacher)):
    query = db.query(Grade).filter(Grade.class_id == class_id)
    if subject_id:
        query = query.filter(Grade.subject_id == subject_id)
    grades = query.all()
    if not grades:
        return {"average": 0, "highest": 0, "lowest": 0, "pass_rate": 0}

    scores = [(g.score / g.max_score) * 100 for g in grades]
    passing = sum(1 for s in scores if s >= 50)
    return {
        "average": round(sum(scores) / len(scores), 2),
        "highest": round(max(scores), 2),
        "lowest": round(min(scores), 2),
        "pass_rate": round((passing / len(scores)) * 100, 2),
        "total_records": len(grades),
        "distribution": {
            "A": sum(1 for s in scores if s >= 80),
            "B": sum(1 for s in scores if 70 <= s < 80),
            "C": sum(1 for s in scores if 60 <= s < 70),
            "D": sum(1 for s in scores if 50 <= s < 60),
            "F": sum(1 for s in scores if s < 50),
        }
    }


# ─── Attendance ───────────────────────────────────────────────────────────────
attendance_router = APIRouter(prefix="/attendance", tags=["Attendance"])

@attendance_router.get("/", response_model=List[AttendanceResponse])
def list_attendance(
    student_id: Optional[int] = None,
    class_id: Optional[int] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Attendance)
    if current_user.role == RoleEnum.student and current_user.student_profile:
        query = query.filter(Attendance.student_id == current_user.student_profile.id)
    elif student_id:
        query = query.filter(Attendance.student_id == student_id)
    if class_id:
        query = query.filter(Attendance.class_id == class_id)
    if from_date:
        query = query.filter(Attendance.date >= from_date)
    if to_date:
        query = query.filter(Attendance.date <= to_date)
    return query.order_by(Attendance.date.desc()).all()


@attendance_router.post("/bulk", status_code=201)
def record_bulk_attendance(
    records: List[AttendanceCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher),
):
    teacher = current_user.teacher_profile
    teacher_id = teacher.id if teacher else None
    created = []
    for rec in records:
        existing = db.query(Attendance).filter(
            Attendance.student_id == rec.student_id,
            Attendance.class_id == rec.class_id,
            Attendance.date == rec.date,
        ).first()
        if existing:
            existing.status = rec.status
            existing.notes = rec.notes
        else:
            att = Attendance(**rec.model_dump(), recorded_by_id=teacher_id)
            db.add(att)
            created.append(att)
    db.commit()
    return {"message": f"Recorded {len(records)} attendance entries"}


# ─── Announcements ────────────────────────────────────────────────────────────
announcements_router = APIRouter(prefix="/announcements", tags=["Announcements"])

@announcements_router.get("/", response_model=List[AnnouncementResponse])
def list_announcements(
    skip: int = 0, limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Announcement).filter(
        Announcement.is_active == True
    ).order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc()).offset(skip).limit(limit).all()


@announcements_router.post("/", response_model=AnnouncementResponse, status_code=201)
def create_announcement(
    data: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher),
):
    teacher = current_user.teacher_profile
    ann = Announcement(
        **data.model_dump(),
        created_by_teacher_id=teacher.id if teacher else None,
        created_by_admin_id=current_user.id if current_user.role in [RoleEnum.admin, RoleEnum.super_admin] else None,
    )
    db.add(ann)
    db.commit()
    db.refresh(ann)
    return ann


@announcements_router.delete("/{announcement_id}")
def delete_announcement(announcement_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    ann = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    ann.is_active = False
    db.commit()
    return {"message": "Deleted"}


# ─── Fees ─────────────────────────────────────────────────────────────────────
fees_router = APIRouter(prefix="/fees", tags=["Fees"])

@fees_router.get("/", response_model=List[FeeResponse])
def list_fees(
    student_id: Optional[int] = None,
    status: Optional[FeeStatusEnum] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Fee)
    if current_user.role == RoleEnum.student and current_user.student_profile:
        query = query.filter(Fee.student_id == current_user.student_profile.id)
    elif student_id:
        query = query.filter(Fee.student_id == student_id)
    if status:
        query = query.filter(Fee.status == status)
    return query.order_by(Fee.due_date.desc()).all()


@fees_router.post("/", response_model=FeeResponse, status_code=201)
def create_fee(data: FeeCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    fee = Fee(**data.model_dump())
    db.add(fee)
    db.commit()
    db.refresh(fee)
    return fee


@fees_router.post("/{fee_id}/pay", response_model=FeeResponse)
def record_payment(
    fee_id: int,
    payment: FeePayment,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    fee = db.query(Fee).filter(Fee.id == fee_id).first()
    if not fee:
        raise HTTPException(status_code=404, detail="Fee not found")

    fee.paid_amount += payment.paid_amount
    fee.payment_date = date.today()
    if fee.transaction_ref:
        fee.transaction_ref = payment.transaction_ref or fee.transaction_ref
    else:
        fee.transaction_ref = payment.transaction_ref

    if fee.paid_amount >= fee.amount:
        fee.status = FeeStatusEnum.paid
    elif fee.paid_amount > 0:
        fee.status = FeeStatusEnum.partial

    db.commit()
    db.refresh(fee)
    return fee


# ─── Timetable ────────────────────────────────────────────────────────────────
timetable_router = APIRouter(prefix="/timetable", tags=["Timetable"])

@timetable_router.get("/{class_id}", response_model=List[TimetableSlotResponse])
def get_timetable(class_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(TimetableSlot).filter(TimetableSlot.class_id == class_id).order_by(
        TimetableSlot.day_of_week, TimetableSlot.start_time
    ).all()


@timetable_router.post("/", response_model=TimetableSlotResponse, status_code=201)
def create_timetable_slot(data: TimetableSlotCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    slot = TimetableSlot(**data.model_dump())
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


# ─── Notifications ────────────────────────────────────────────────────────────
notifications_router = APIRouter(prefix="/notifications", tags=["Notifications"])

@notifications_router.get("/", response_model=List[NotificationResponse])
def list_notifications(
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.models import Notification
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if unread_only:
        query = query.filter(Notification.is_read == False)
    return query.order_by(Notification.created_at.desc()).limit(50).all()


@notifications_router.put("/{notification_id}/read")
def mark_read(notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.models.models import Notification
    notif = db.query(Notification).filter(
        Notification.id == notification_id, Notification.user_id == current_user.id
    ).first()
    if notif:
        notif.is_read = True
        db.commit()
    return {"message": "Marked as read"}


@notifications_router.put("/read-all")
def mark_all_read(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.models.models import Notification
    db.query(Notification).filter(
        Notification.user_id == current_user.id, Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"message": "All marked as read"}


# ─── Admin Dashboard ──────────────────────────────────────────────────────────
admin_router = APIRouter(prefix="/admin", tags=["Admin"])

@admin_router.get("/dashboard")
def admin_dashboard(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    from app.models.models import Student, Teacher, Class, Subject, Fee, Attendance, ActivityLog
    from sqlalchemy import func
    from datetime import timedelta

    today = date.today()
    week_ago = today - timedelta(days=7)

    # Attendance today
    att_today = db.query(Attendance).filter(Attendance.date == today).count()
    att_present_today = db.query(Attendance).filter(
        Attendance.date == today, Attendance.status == "present"
    ).count()

    # Fee stats
    total_fees = db.query(func.sum(Fee.amount)).scalar() or 0
    collected_fees = db.query(func.sum(Fee.paid_amount)).scalar() or 0

    # Recent logs
    recent_logs = db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(10).all()

    return {
        "stats": {
            "total_students": db.query(Student).count(),
            "total_teachers": db.query(Teacher).count(),
            "total_classes": db.query(Class).filter(Class.is_active == True).count(),
            "total_subjects": db.query(Subject).filter(Subject.is_active == True).count(),
        },
        "attendance_today": {
            "total": att_today,
            "present": att_present_today,
            "rate": round((att_present_today / att_today * 100) if att_today > 0 else 0, 1),
        },
        "fees": {
            "total": float(total_fees),
            "collected": float(collected_fees),
            "outstanding": float(total_fees - collected_fees),
            "collection_rate": round((collected_fees / total_fees * 100) if total_fees > 0 else 0, 1),
        },
        "recent_activity": [
            {"action": log.action, "resource": log.resource, "time": log.created_at.isoformat()}
            for log in recent_logs
        ],
    }
