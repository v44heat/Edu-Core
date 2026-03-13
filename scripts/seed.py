"""
Seed script to populate the database with sample data.
Run: python -m scripts.seed
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, datetime, timedelta, time
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.core.database import Base
from app.core.security import get_password_hash
from app.models.models import (
    User, Student, Teacher, Class, Subject, SubjectAssignment,
    Enrollment, Assignment, Grade, Attendance, Announcement, Fee,
    TimetableSlot, Notification,
    RoleEnum, GenderEnum, FeeStatusEnum, AttendanceStatusEnum
)

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("🌱 Seeding database...")

        # ── Users ──────────────────────────────────────────────────────────────
        users_data = [
            {"email": "superadmin@school.edu", "username": "superadmin", "full_name": "Super Administrator", "role": RoleEnum.super_admin, "password": "Admin@1234"},
            {"email": "admin@school.edu", "username": "admin", "full_name": "School Administrator", "role": RoleEnum.admin, "password": "Admin@1234"},
            {"email": "john.doe@school.edu", "username": "john.doe", "full_name": "John Doe", "role": RoleEnum.teacher, "password": "Teacher@1234"},
            {"email": "jane.smith@school.edu", "username": "jane.smith", "full_name": "Jane Smith", "role": RoleEnum.teacher, "password": "Teacher@1234"},
            {"email": "bob.johnson@school.edu", "username": "bob.johnson", "full_name": "Bob Johnson", "role": RoleEnum.teacher, "password": "Teacher@1234"},
            {"email": "alice@school.edu", "username": "alice", "full_name": "Alice Thompson", "role": RoleEnum.student, "password": "Student@1234"},
            {"email": "charlie@school.edu", "username": "charlie", "full_name": "Charlie Brown", "role": RoleEnum.student, "password": "Student@1234"},
            {"email": "diana@school.edu", "username": "diana", "full_name": "Diana Prince", "role": RoleEnum.student, "password": "Student@1234"},
            {"email": "evan@school.edu", "username": "evan", "full_name": "Evan Williams", "role": RoleEnum.student, "password": "Student@1234"},
            {"email": "fiona@school.edu", "username": "fiona", "full_name": "Fiona Green", "role": RoleEnum.student, "password": "Student@1234"},
        ]

        users = {}
        for u in users_data:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if not existing:
                user = User(
                    email=u["email"], username=u["username"],
                    full_name=u["full_name"], role=u["role"],
                    hashed_password=get_password_hash(u["password"]),
                    is_active=True, is_verified=True,
                )
                db.add(user)
                db.flush()
                users[u["username"]] = user
                print(f"  ✓ User: {u['username']} ({u['role'].value})")
            else:
                users[u["username"]] = existing

        db.commit()

        # ── Teachers ───────────────────────────────────────────────────────────
        teachers_data = [
            {"username": "john.doe", "teacher_id": "TCH001", "qualification": "MSc Mathematics", "specialization": "Mathematics", "hire_date": date(2018, 8, 1), "salary": 55000},
            {"username": "jane.smith", "teacher_id": "TCH002", "qualification": "BSc Physics", "specialization": "Science", "hire_date": date(2019, 9, 1), "salary": 52000},
            {"username": "bob.johnson", "teacher_id": "TCH003", "qualification": "BA English Literature", "specialization": "English", "hire_date": date(2020, 1, 15), "salary": 50000},
        ]
        teachers = {}
        for t in teachers_data:
            if t["username"] in users:
                existing = db.query(Teacher).filter(Teacher.teacher_id == t["teacher_id"]).first()
                if not existing:
                    teacher = Teacher(
                        user_id=users[t["username"]].id,
                        teacher_id=t["teacher_id"],
                        qualification=t["qualification"],
                        specialization=t["specialization"],
                        hire_date=t["hire_date"],
                        salary=t["salary"],
                        gender=GenderEnum.male,
                    )
                    db.add(teacher)
                    db.flush()
                    teachers[t["username"]] = teacher
                else:
                    teachers[t["username"]] = existing

        db.commit()

        # ── Classes ────────────────────────────────────────────────────────────
        classes_data = [
            {"name": "Grade 10 - A", "grade_level": "10", "section": "A", "academic_year": "2024-2025", "room_number": "101"},
            {"name": "Grade 10 - B", "grade_level": "10", "section": "B", "academic_year": "2024-2025", "room_number": "102"},
            {"name": "Grade 11 - A", "grade_level": "11", "section": "A", "academic_year": "2024-2025", "room_number": "201"},
        ]
        classes = {}
        for c in classes_data:
            existing = db.query(Class).filter(Class.name == c["name"], Class.academic_year == c["academic_year"]).first()
            if not existing:
                teacher_key = list(teachers.keys())[list(classes_data).index(c) % len(teachers)]
                cls = Class(
                    **c,
                    teacher_id=teachers[teacher_key].id if teacher_key in teachers else None,
                )
                db.add(cls)
                db.flush()
                classes[c["name"]] = cls
            else:
                classes[c["name"]] = existing

        db.commit()

        # ── Subjects ──────────────────────────────────────────────────────────
        subjects_data = [
            {"name": "Mathematics", "code": "MATH10", "credit_hours": 4, "grade_level": "10"},
            {"name": "Physics", "code": "PHY10", "credit_hours": 3, "grade_level": "10"},
            {"name": "English Language", "code": "ENG10", "credit_hours": 3, "grade_level": "10"},
            {"name": "Chemistry", "code": "CHEM10", "credit_hours": 3, "grade_level": "10"},
            {"name": "History", "code": "HIST10", "credit_hours": 2, "grade_level": "10"},
            {"name": "Advanced Mathematics", "code": "MATH11", "credit_hours": 4, "grade_level": "11"},
        ]
        subjects = {}
        for s in subjects_data:
            existing = db.query(Subject).filter(Subject.code == s["code"]).first()
            if not existing:
                subj = Subject(**s)
                db.add(subj)
                db.flush()
                subjects[s["code"]] = subj
            else:
                subjects[s["code"]] = existing

        db.commit()

        # ── Students ──────────────────────────────────────────────────────────
        first_class = list(classes.values())[0]
        students_data = [
            {"username": "alice", "student_id": "STU001", "class_name": "Grade 10 - A"},
            {"username": "charlie", "student_id": "STU002", "class_name": "Grade 10 - A"},
            {"username": "diana", "student_id": "STU003", "class_name": "Grade 10 - B"},
            {"username": "evan", "student_id": "STU004", "class_name": "Grade 10 - B"},
            {"username": "fiona", "student_id": "STU005", "class_name": "Grade 11 - A"},
        ]
        students = {}
        for s in students_data:
            if s["username"] in users:
                existing = db.query(Student).filter(Student.student_id == s["student_id"]).first()
                if not existing:
                    cls = classes.get(s["class_name"], first_class)
                    student = Student(
                        user_id=users[s["username"]].id,
                        student_id=s["student_id"],
                        class_id=cls.id,
                        admission_date=date(2022, 9, 1),
                        date_of_birth=date(2007, 3, 15),
                        gender=GenderEnum.female,
                        parent_name="Parent Name",
                        parent_phone="+1-555-0100",
                    )
                    db.add(student)
                    db.flush()
                    students[s["username"]] = student
                else:
                    students[s["username"]] = existing

        db.commit()

        # ── Enrollments ───────────────────────────────────────────────────────
        grade10_subjects = ["MATH10", "PHY10", "ENG10", "CHEM10", "HIST10"]
        for username, student in students.items():
            cls = db.query(Class).filter(Class.id == student.class_id).first()
            level = cls.grade_level if cls else "10"
            subj_codes = grade10_subjects if level == "10" else ["MATH11"]
            for code in subj_codes:
                if code in subjects:
                    existing = db.query(Enrollment).filter(
                        Enrollment.student_id == student.id,
                        Enrollment.subject_id == subjects[code].id
                    ).first()
                    if not existing:
                        enr = Enrollment(
                            student_id=student.id,
                            class_id=student.class_id,
                            subject_id=subjects[code].id,
                            academic_year="2024-2025",
                            enrollment_date=date(2024, 9, 1),
                        )
                        db.add(enr)

        db.commit()

        # ── Grades ────────────────────────────────────────────────────────────
        import random
        grade_letters = lambda s: "A+" if s>=90 else "A" if s>=80 else "B+" if s>=75 else "B" if s>=70 else "C+" if s>=65 else "C" if s>=60 else "D" if s>=50 else "F"
        for username, student in students.items():
            if student.class_id:
                for code, subj in list(subjects.items())[:4]:
                    for exam in [("Midterm Exam", "midterm"), ("Final Exam", "final"), ("Quiz 1", "quiz")]:
                        score = random.uniform(55, 98)
                        existing = db.query(Grade).filter(
                            Grade.student_id == student.id, Grade.subject_id == subj.id, Grade.exam_name == exam[0]
                        ).first()
                        if not existing:
                            g = Grade(
                                student_id=student.id, subject_id=subj.id, class_id=student.class_id,
                                exam_name=exam[0], exam_type=exam[1], score=round(score, 1),
                                max_score=100.0, grade_letter=grade_letters(score),
                                academic_year="2024-2025", term="Term 1",
                            )
                            db.add(g)

        db.commit()

        # ── Attendance ────────────────────────────────────────────────────────
        today = date.today()
        for i in range(30):
            att_date = today - timedelta(days=i)
            if att_date.weekday() < 5:  # weekdays only
                for username, student in students.items():
                    if student.class_id:
                        existing = db.query(Attendance).filter(
                            Attendance.student_id == student.id, Attendance.date == att_date
                        ).first()
                        if not existing:
                            rand = random.random()
                            status = AttendanceStatusEnum.present if rand > 0.15 else (
                                AttendanceStatusEnum.absent if rand > 0.05 else AttendanceStatusEnum.late
                            )
                            att = Attendance(
                                student_id=student.id, class_id=student.class_id,
                                date=att_date, status=status,
                            )
                            db.add(att)

        db.commit()

        # ── Assignments ───────────────────────────────────────────────────────
        teacher_list = list(teachers.values())
        if teacher_list and subjects:
            first_class_obj = list(classes.values())[0]
            math_subj = subjects.get("MATH10")
            eng_subj = subjects.get("ENG10")
            for i, (title, subj, days) in enumerate([
                ("Algebra Problem Set", math_subj, 7),
                ("Essay: Modern Literature", eng_subj, 14),
                ("Calculus Quiz Prep", math_subj, 3),
                ("Reading Comprehension", eng_subj, 5),
            ]):
                if subj:
                    existing = db.query(Assignment).filter(Assignment.title == title).first()
                    if not existing:
                        asgn = Assignment(
                            title=title, description=f"Complete all tasks for {title}",
                            subject_id=subj.id, class_id=first_class_obj.id,
                            teacher_id=teacher_list[i % len(teacher_list)].id,
                            due_date=datetime.utcnow() + timedelta(days=days),
                            max_score=100.0,
                        )
                        db.add(asgn)

        db.commit()

        # ── Fees ──────────────────────────────────────────────────────────────
        fee_types = [
            ("Tuition Fee", 1500.0), ("Exam Fee", 50.0),
            ("Library Fee", 30.0), ("Sports Fee", 40.0)
        ]
        for username, student in students.items():
            for fee_type, amount in fee_types:
                existing = db.query(Fee).filter(
                    Fee.student_id == student.id, Fee.fee_type == fee_type,
                    Fee.academic_year == "2024-2025"
                ).first()
                if not existing:
                    paid = amount if random.random() > 0.3 else (amount * random.uniform(0, 0.8))
                    status = FeeStatusEnum.paid if paid >= amount else (FeeStatusEnum.partial if paid > 0 else FeeStatusEnum.pending)
                    fee = Fee(
                        student_id=student.id, fee_type=fee_type, amount=amount,
                        paid_amount=round(paid, 2), due_date=date(2024, 10, 31),
                        status=status, academic_year="2024-2025", term="Term 1",
                    )
                    db.add(fee)

        db.commit()

        # ── Announcements ─────────────────────────────────────────────────────
        ann_data = [
            ("Welcome Back to School!", "We are excited to welcome all students and staff back for the new academic year 2024-2025.", True),
            ("Mid-Term Exam Schedule", "The mid-term examinations will be held from October 15-19, 2024. Please check the exam timetable.", False),
            ("School Sports Day", "Annual Sports Day will be held on November 10th. All students are encouraged to participate.", False),
            ("Library Book Fair", "The annual book fair will be at the school library from October 1-5. Get great books at discounted prices!", False),
        ]
        for title, content, pinned in ann_data:
            existing = db.query(Announcement).filter(Announcement.title == title).first()
            if not existing:
                ann = Announcement(title=title, content=content, is_pinned=pinned, is_active=True)
                db.add(ann)

        db.commit()

        # ── Timetable ─────────────────────────────────────────────────────────
        if classes and subjects and teachers:
            first_cls = list(classes.values())[0]
            slots = [
                (0, time(8, 0), time(9, 0), "MATH10", "john.doe"),
                (0, time(9, 0), time(10, 0), "ENG10", "bob.johnson"),
                (0, time(10, 30), time(11, 30), "PHY10", "jane.smith"),
                (1, time(8, 0), time(9, 0), "CHEM10", "jane.smith"),
                (1, time(9, 0), time(10, 0), "MATH10", "john.doe"),
                (2, time(8, 0), time(9, 0), "ENG10", "bob.johnson"),
                (2, time(9, 0), time(10, 0), "PHY10", "jane.smith"),
                (3, time(8, 0), time(9, 0), "MATH10", "john.doe"),
                (4, time(8, 0), time(9, 0), "HIST10", "bob.johnson"),
            ]
            for day, start, end, subj_code, teacher_key in slots:
                if subj_code in subjects and teacher_key in teachers:
                    existing = db.query(TimetableSlot).filter(
                        TimetableSlot.class_id == first_cls.id,
                        TimetableSlot.day_of_week == day,
                        TimetableSlot.start_time == start,
                    ).first()
                    if not existing:
                        slot = TimetableSlot(
                            class_id=first_cls.id, subject_id=subjects[subj_code].id,
                            teacher_id=teachers[teacher_key].id, day_of_week=day,
                            start_time=start, end_time=end, academic_year="2024-2025",
                        )
                        db.add(slot)

        db.commit()
        print("\n✅ Database seeded successfully!")
        print("\n📋 Login Credentials:")
        print("  Super Admin: superadmin / Admin@1234")
        print("  Admin:       admin / Admin@1234")
        print("  Teacher:     john.doe / Teacher@1234")
        print("  Student:     alice / Student@1234")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
