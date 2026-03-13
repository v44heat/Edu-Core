-- ============================================================
--  EduCore School Management System — PostgreSQL Schema
--  Run: psql -U postgres -d school_mgmt -f schema.sql
-- ============================================================

CREATE DATABASE school_mgmt;
\c school_mgmt;

-- Enable pgcrypto for UUID generation
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ── ENUMS ────────────────────────────────────────────────────────────────────

CREATE TYPE role_enum AS ENUM ('super_admin','admin','teacher','student');
CREATE TYPE gender_enum AS ENUM ('male','female','other');
CREATE TYPE attendance_status AS ENUM ('present','absent','late','excused');
CREATE TYPE submission_status AS ENUM ('submitted','graded','late','missing');
CREATE TYPE fee_status AS ENUM ('pending','paid','overdue','partial');
CREATE TYPE announcement_target AS ENUM ('all','students','teachers','class_specific');

-- ── USERS ────────────────────────────────────────────────────────────────────

CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) UNIQUE NOT NULL,
    username        VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255) NOT NULL,
    role            role_enum NOT NULL DEFAULT 'student',
    phone           VARCHAR(20),
    avatar_url      VARCHAR(500),
    is_active       BOOLEAN DEFAULT TRUE,
    is_verified     BOOLEAN DEFAULT FALSE,
    last_login      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);

-- ── TEACHERS ─────────────────────────────────────────────────────────────────

CREATE TABLE teachers (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    teacher_id      VARCHAR(20) UNIQUE NOT NULL,
    date_of_birth   DATE,
    gender          gender_enum,
    address         TEXT,
    qualification   VARCHAR(255),
    specialization  VARCHAR(255),
    hire_date       DATE,
    salary          DECIMAL(10,2),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_teachers_user_id ON teachers(user_id);
CREATE INDEX idx_teachers_teacher_id ON teachers(teacher_id);

-- ── CLASSES ──────────────────────────────────────────────────────────────────

CREATE TABLE classes (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    grade_level     VARCHAR(20) NOT NULL,
    section         VARCHAR(10),
    academic_year   VARCHAR(20) NOT NULL,
    teacher_id      INTEGER REFERENCES teachers(id) ON DELETE SET NULL,
    room_number     VARCHAR(20),
    max_students    INTEGER DEFAULT 40,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_classes_academic_year ON classes(academic_year);
CREATE INDEX idx_classes_teacher_id ON classes(teacher_id);

-- ── STUDENTS ─────────────────────────────────────────────────────────────────

CREATE TABLE students (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    student_id      VARCHAR(20) UNIQUE NOT NULL,
    date_of_birth   DATE,
    gender          gender_enum,
    address         TEXT,
    parent_name     VARCHAR(255),
    parent_phone    VARCHAR(20),
    parent_email    VARCHAR(255),
    admission_date  DATE,
    class_id        INTEGER REFERENCES classes(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_students_user_id ON students(user_id);
CREATE INDEX idx_students_student_id ON students(student_id);
CREATE INDEX idx_students_class_id ON students(class_id);

-- ── SUBJECTS ─────────────────────────────────────────────────────────────────

CREATE TABLE subjects (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    code            VARCHAR(20) UNIQUE NOT NULL,
    description     TEXT,
    credit_hours    INTEGER DEFAULT 1,
    grade_level     VARCHAR(20),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_subjects_code ON subjects(code);

-- ── SUBJECT ASSIGNMENTS (Teacher → Subject × Class) ──────────────────────────

CREATE TABLE subject_assignments (
    id              SERIAL PRIMARY KEY,
    teacher_id      INTEGER REFERENCES teachers(id) ON DELETE CASCADE,
    subject_id      INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    class_id        INTEGER REFERENCES classes(id) ON DELETE CASCADE,
    academic_year   VARCHAR(20) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(teacher_id, subject_id, class_id, academic_year)
);

-- ── ENROLLMENTS ──────────────────────────────────────────────────────────────

CREATE TABLE enrollments (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER REFERENCES students(id) ON DELETE CASCADE,
    class_id        INTEGER REFERENCES classes(id) ON DELETE CASCADE,
    subject_id      INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    academic_year   VARCHAR(20) NOT NULL,
    enrollment_date DATE,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(student_id, subject_id, academic_year)
);

CREATE INDEX idx_enrollments_student ON enrollments(student_id);
CREATE INDEX idx_enrollments_class ON enrollments(class_id);

-- ── ASSIGNMENTS ───────────────────────────────────────────────────────────────

CREATE TABLE assignments (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    subject_id      INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    class_id        INTEGER REFERENCES classes(id) ON DELETE CASCADE,
    teacher_id      INTEGER REFERENCES teachers(id) ON DELETE CASCADE,
    due_date        TIMESTAMPTZ NOT NULL,
    max_score       DECIMAL(6,2) DEFAULT 100.0,
    file_url        VARCHAR(500),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_assignments_class ON assignments(class_id);
CREATE INDEX idx_assignments_teacher ON assignments(teacher_id);
CREATE INDEX idx_assignments_due ON assignments(due_date);

-- ── SUBMISSIONS ───────────────────────────────────────────────────────────────

CREATE TABLE submissions (
    id              SERIAL PRIMARY KEY,
    assignment_id   INTEGER REFERENCES assignments(id) ON DELETE CASCADE,
    student_id      INTEGER REFERENCES students(id) ON DELETE CASCADE,
    file_url        VARCHAR(500),
    notes           TEXT,
    status          submission_status DEFAULT 'submitted',
    score           DECIMAL(6,2),
    feedback        TEXT,
    submitted_at    TIMESTAMPTZ DEFAULT NOW(),
    graded_at       TIMESTAMPTZ,
    UNIQUE(assignment_id, student_id)
);

CREATE INDEX idx_submissions_assignment ON submissions(assignment_id);
CREATE INDEX idx_submissions_student ON submissions(student_id);

-- ── GRADES ────────────────────────────────────────────────────────────────────

CREATE TABLE grades (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER REFERENCES students(id) ON DELETE CASCADE,
    subject_id      INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    class_id        INTEGER REFERENCES classes(id) ON DELETE CASCADE,
    exam_name       VARCHAR(100) NOT NULL,
    exam_type       VARCHAR(50),
    score           DECIMAL(6,2) NOT NULL,
    max_score       DECIMAL(6,2) DEFAULT 100.0,
    grade_letter    VARCHAR(5),
    academic_year   VARCHAR(20),
    term            VARCHAR(20),
    remarks         TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_grades_student ON grades(student_id);
CREATE INDEX idx_grades_subject ON grades(subject_id);
CREATE INDEX idx_grades_class ON grades(class_id);
CREATE INDEX idx_grades_academic_year ON grades(academic_year);

-- ── ATTENDANCE ────────────────────────────────────────────────────────────────

CREATE TABLE attendance (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER REFERENCES students(id) ON DELETE CASCADE,
    class_id        INTEGER REFERENCES classes(id) ON DELETE CASCADE,
    subject_id      INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
    date            DATE NOT NULL,
    status          attendance_status NOT NULL,
    recorded_by_id  INTEGER REFERENCES teachers(id) ON DELETE SET NULL,
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_attendance_student ON attendance(student_id);
CREATE INDEX idx_attendance_date ON attendance(date);
CREATE INDEX idx_attendance_class ON attendance(class_id);
CREATE UNIQUE INDEX idx_attendance_unique ON attendance(student_id, class_id, date);

-- ── TIMETABLE ─────────────────────────────────────────────────────────────────

CREATE TABLE timetable_slots (
    id              SERIAL PRIMARY KEY,
    class_id        INTEGER REFERENCES classes(id) ON DELETE CASCADE,
    subject_id      INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    teacher_id      INTEGER REFERENCES teachers(id) ON DELETE SET NULL,
    day_of_week     SMALLINT NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
    start_time      TIME NOT NULL,
    end_time        TIME NOT NULL,
    room            VARCHAR(50),
    academic_year   VARCHAR(20),
    CHECK (start_time < end_time)
);

CREATE INDEX idx_timetable_class ON timetable_slots(class_id);
CREATE INDEX idx_timetable_day ON timetable_slots(day_of_week);

-- ── ANNOUNCEMENTS ─────────────────────────────────────────────────────────────

CREATE TABLE announcements (
    id                      SERIAL PRIMARY KEY,
    title                   VARCHAR(255) NOT NULL,
    content                 TEXT NOT NULL,
    target_audience         announcement_target DEFAULT 'all',
    target_class_id         INTEGER REFERENCES classes(id) ON DELETE SET NULL,
    created_by_teacher_id   INTEGER REFERENCES teachers(id) ON DELETE SET NULL,
    created_by_admin_id     INTEGER REFERENCES users(id) ON DELETE SET NULL,
    is_pinned               BOOLEAN DEFAULT FALSE,
    is_active               BOOLEAN DEFAULT TRUE,
    expires_at              TIMESTAMPTZ,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_announcements_active ON announcements(is_active);
CREATE INDEX idx_announcements_target ON announcements(target_audience);

-- ── FEES ──────────────────────────────────────────────────────────────────────

CREATE TABLE fees (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER REFERENCES students(id) ON DELETE CASCADE,
    fee_type        VARCHAR(100) NOT NULL,
    amount          DECIMAL(10,2) NOT NULL,
    paid_amount     DECIMAL(10,2) DEFAULT 0.0,
    due_date        DATE NOT NULL,
    payment_date    DATE,
    status          fee_status DEFAULT 'pending',
    academic_year   VARCHAR(20),
    term            VARCHAR(20),
    transaction_ref VARCHAR(100),
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_fees_student ON fees(student_id);
CREATE INDEX idx_fees_status ON fees(status);
CREATE INDEX idx_fees_due_date ON fees(due_date);

-- ── NOTIFICATIONS ─────────────────────────────────────────────────────────────

CREATE TABLE notifications (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title       VARCHAR(255) NOT NULL,
    message     TEXT NOT NULL,
    type        VARCHAR(50),
    is_read     BOOLEAN DEFAULT FALSE,
    related_id  INTEGER,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read);

-- ── ACTIVITY LOGS ─────────────────────────────────────────────────────────────

CREATE TABLE activity_logs (
    id          BIGSERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action      VARCHAR(100) NOT NULL,
    resource    VARCHAR(100),
    resource_id INTEGER,
    details     JSONB,
    ip_address  VARCHAR(45),
    user_agent  VARCHAR(500),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_logs_user ON activity_logs(user_id);
CREATE INDEX idx_logs_created ON activity_logs(created_at DESC);

-- ============================================================
--  Views
-- ============================================================

CREATE VIEW student_attendance_summary AS
SELECT
    s.id AS student_id,
    u.full_name,
    s.student_id AS student_code,
    COUNT(*) AS total_days,
    COUNT(*) FILTER (WHERE a.status = 'present') AS present_days,
    COUNT(*) FILTER (WHERE a.status = 'absent') AS absent_days,
    ROUND(COUNT(*) FILTER (WHERE a.status = 'present')::NUMERIC / NULLIF(COUNT(*), 0) * 100, 2) AS attendance_rate
FROM students s
JOIN users u ON s.user_id = u.id
LEFT JOIN attendance a ON s.id = a.student_id
GROUP BY s.id, u.full_name, s.student_id;


CREATE VIEW class_grade_summary AS
SELECT
    c.id AS class_id,
    c.name AS class_name,
    sub.id AS subject_id,
    sub.name AS subject_name,
    COUNT(g.id) AS total_grades,
    ROUND(AVG(g.score / g.max_score * 100), 2) AS average_pct,
    MAX(g.score / g.max_score * 100) AS highest_pct,
    MIN(g.score / g.max_score * 100) AS lowest_pct
FROM classes c
JOIN grades g ON g.class_id = c.id
JOIN subjects sub ON g.subject_id = sub.id
GROUP BY c.id, c.name, sub.id, sub.name;
