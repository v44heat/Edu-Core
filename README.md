# 🎓 EduCore — School Management System

<div align="center">

![EduCore Banner](https://img.shields.io/badge/EduCore-School%20Management%20System-2563eb?style=for-the-badge&logoColor=white)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-cc0000?style=flat-square)](https://sqlalchemy.org)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)

**A production-ready, full-stack School Management System with role-based dashboards for Super Admins, Admins, Teachers, and Students.**

[Features](#-features) · [Screenshots](#-screenshots) · [Quick Start](#-quick-start) · [API Docs](#-api-endpoints) · [Contributing](#-contributing)

</div>

---

## 📸 Screenshots

### 🔐 Login Page
> Split-panel design with quick demo login buttons for all four roles — one click to log in as Super Admin, Admin, Teacher, or Student

<img width="1909" height="1072" alt="EduCore — School Management System - Google Chrome 13_03_2026 05_08_45 AM" src="https://github.com/user-attachments/assets/b505ba2f-47ad-43fe-b900-6f4fe5b49916" />
<img width="1909" height="1072" alt="EduCore — School Management System - Google Chrome 13_03_2026 05_08_34 AM" src="https://github.com/user-attachments/assets/85791b94-c454-4ee0-89b6-8fcec3307189" />
<img width="1909" height="1072" alt="EduCore — School Management System - Google Chrome 13_03_2026 05_08_25 AM" src="https://github.com/user-attachments/assets/b143449b-c602-4cd1-b5ac-6721ff84d577" />
<img width="1909" height="1072" alt="EduCore — School Management System - Google Chrome 13_03_2026 05_08_06 AM" src="https://github.com/user-attachments/assets/8ad29234-2039-46a2-b483-cb6b6ee3a1be" />
<img width="1909" height="1072" alt="EduCore — School Management System - Google Chrome 13_03_2026 05_07_47 AM" src="https://github.com/user-attachments/assets/27d2df0a-dc86-49ca-8c05-7c5f77e33747" />


---

### 📊 Admin Dashboard — Super Admin View
> Personalized greeting, live stats cards (Students, Teachers, Classes, Subjects), weekly attendance stacked bar chart, grade distribution donut chart, recent announcements, and activity log

<img width="1909" height="1072" alt="EduCore — School Management System - Google Chrome 13_03_2026 05_08_25 AM" src="https://github.com/user-attachments/assets/12d22b68-555b-4f23-8ae4-df6fa4a5b003" />


---

### 🎒 Student Dashboard — Alice Thompson's View
> Role-aware navigation — students see only their relevant sections. Admin-only pages (Teachers, Classes, Subjects) are automatically hidden from the sidebar
>

<img width="1909" height="1072" alt="EduCore — School Management System - Google Chrome 13_03_2026 05_08_06 AM" src="https://github.com/user-attachments/assets/1a96d15e-0e80-4e07-b889-eab0c0e781a8" />



---

### 👥 Students Management
> Searchable student records table with avatar initials, student IDs, class assignments, gender badges, and attendance progress bars. Admins get the "+ Add Student" button

<img width="1909" height="1072" alt="EduCore — School Management System - Google Chrome 13_03_2026 05_08_34 AM" src="https://github.com/user-attachments/assets/2e5555fb-2013-4d21-8747-3edc40741e32" />


---

### 💳 Fees Management
> Full fee tracking with amount, paid amount, outstanding balance highlighted in red, due dates, status badges (Paid ✓ / Partial / Pending), and one-click green Pay buttons

<img width="1909" height="1072" alt="EduCore — School Management System - Google Chrome 13_03_2026 05_08_45 AM" src="https://github.com/user-attachments/assets/63fcedd4-fc19-44d4-9156-df15fefb9b7e" />


---

## ✨ Features

### 🔐 Authentication & Security
- JWT access tokens (60 min) + refresh tokens (7 days)
- bcrypt password hashing
- Role-based access control (RBAC) — 4 distinct roles
- Full activity audit logging for Super Admin
- SQL injection protection via SQLAlchemy ORM
- Input validation via Pydantic v2

### 👥 Four User Roles

| Role | Capabilities |
|------|-------------|
| 🔴 **Super Admin** | Full system control, manage all admins, view system logs, database oversight |
| 🟣 **Admin** | Manage users, classes, subjects, fees, enrollments, announcements |
| 🟢 **Teacher** | Upload assignments, grade submissions, record attendance, post announcements |
| 🔵 **Student** | View grades, submit assignments, check timetable, view fees & announcements |

### 📚 Core Modules
- **Dashboard** — Live stats, attendance charts, grade distribution, announcements, activity log
- **Students** — Profiles, enrollment, parent contact info, attendance tracking
- **Teachers** — Staff profiles, class assignments, subject management
- **Classes** — Sections, academic years, room assignments, visual card layout
- **Subjects** — Course catalog with credit hours and grade levels
- **Assignments** — File uploads, due dates, auto late-detection, submission tracking
- **Grades** — Exam results with automatic A+/A/B+/B/C+/C/D/F letter grade calculation
- **Attendance** — Bulk daily recording with present / absent / late / excused status
- **Fees** — Payment tracking, partial payments, one-click payment recording
- **Announcements** — Pinned notices, role-targeted messaging (all / students / teachers)
- **Notifications** — In-app alerts with unread dot indicator
- **Activity Logs** — Full audit trail (Super Admin only)

### 🎨 UI/UX Highlights
- Fully responsive — works on mobile and desktop
- Dark sidebar with role-aware navigation
- Interactive Chart.js analytics (stacked bar + doughnut charts)
- Modal forms for all create/edit operations
- Toast notifications for instant user feedback
- Personalized greeting by time of day and first name

---

## 🏗️ Architecture

```
school_mgmt/
├── main.py                      # FastAPI app entry point
├── requirements.txt             # Python dependencies
├── schema.sql                   # Full PostgreSQL DDL with indexes & views
├── .env.example                 # Environment variables template
│
├── app/
│   ├── api/
│   │   ├── auth.py              # Login, logout, token refresh
│   │   ├── users.py             # User CRUD (Admin+)
│   │   ├── academics.py         # Students, Teachers, Classes, Subjects
│   │   ├── operations.py        # Assignments, Grades, Attendance, Fees, etc.
│   │   └── deps.py              # JWT auth dependencies & RBAC decorators
│   ├── core/
│   │   ├── config.py            # Pydantic settings from .env
│   │   ├── database.py          # SQLAlchemy engine & session factory
│   │   └── security.py          # JWT encode/decode, bcrypt hashing
│   ├── models/
│   │   └── models.py            # 15 SQLAlchemy ORM models
│   ├── schemas/
│   │   └── schemas.py           # Pydantic v2 request/response schemas
│   ├── templates/
│   │   ├── login.html           # Login page
│   │   └── dashboard.html       # Main SPA dashboard
│   └── static/                  # CSS, JS, images
│
└── scripts/
    └── seed.py                  # Sample data seeder
```

### Database — 15 Normalized Tables

```
users ──────────────┬──── students ──────┬──── enrollments
                    │                    ├──── submissions ──── assignments
                    └──── teachers       ├──── grades
                               │         ├──── attendance
                               │         └──── fees
                               │
                          classes ──────── subjects
                               │               │
                               └──── subject_assignments
                               └──── timetable_slots

announcements ── notifications ── activity_logs
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/educore-school-management.git
cd educore-school-management
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt

# Fix bcrypt version conflict (especially on Windows):
pip install bcrypt==4.0.1
```

### 4. Configure Environment

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Edit `.env` — replace `YOUR_PASSWORD` with your PostgreSQL password:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/school_mgmt
SECRET_KEY=your-super-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
DEBUG=True
UPLOAD_DIR=uploads
```

### 5. Create the Database

```bash
psql -U postgres -c "CREATE DATABASE school_mgmt;"
```

### 6. Seed Sample Data

```bash
python -m scripts.seed
```

### 7. Create Static Folder

```bash
# Windows
mkdir app\static

# macOS / Linux
mkdir -p app/static
```

### 8. Run the Server

```bash
uvicorn main:app --reload --port 8000
```

### 9. Open in Browser

| URL | Description |
|-----|-------------|
| http://localhost:8000 | Login page |
| http://localhost:8000/dashboard | Main dashboard |
| http://localhost:8000/api/docs | Swagger interactive API docs |
| http://localhost:8000/api/redoc | ReDoc API reference |

---

## 🔑 Demo Login Credentials

| Role | Username | Password |
|------|----------|----------|
| 🔴 Super Admin | `superadmin` | `Admin@1234` |
| 🟣 Admin | `admin` | `Admin@1234` |
| 🟢 Teacher | `john.doe` | `Teacher@1234` |
| 🔵 Student | `alice` | `Student@1234` |

> All demo accounts are created automatically when you run `python -m scripts.seed`

---

## 🌐 API Endpoints

### Authentication
```http
POST   /api/v1/auth/login              Login and receive JWT tokens
POST   /api/v1/auth/refresh            Refresh expired access token
POST   /api/v1/auth/logout             Logout current session
GET    /api/v1/auth/me                 Get current authenticated user
POST   /api/v1/auth/change-password    Change account password
```

### Users *(Admin+ only)*
```http
GET    /api/v1/users/                  List all users (filterable by role)
POST   /api/v1/users/                  Create new user
GET    /api/v1/users/{id}              Get user by ID
PUT    /api/v1/users/{id}              Update user details
DELETE /api/v1/users/{id}              Delete user (Super Admin only)
GET    /api/v1/users/stats/overview    User count statistics
```

### Academics
```http
GET/POST  /api/v1/students/            List / Create students
GET       /api/v1/students/{id}/dashboard   Student dashboard data
GET/POST  /api/v1/teachers/            List / Create teachers
GET/POST  /api/v1/classes/             List / Create classes
GET       /api/v1/classes/{id}/students     Students in a class
GET/POST  /api/v1/subjects/            List / Create subjects
```

### Operations
```http
GET/POST  /api/v1/assignments/         List / Create assignments
POST      /api/v1/assignments/{id}/upload   Upload assignment file
POST      /api/v1/submissions/         Submit assignment (with file upload)
PUT       /api/v1/submissions/{id}/grade    Grade a submission
GET/POST  /api/v1/grades/              List / Record grades
GET       /api/v1/grades/analytics/{class_id}  Class analytics
GET       /api/v1/attendance/          List attendance records
POST      /api/v1/attendance/bulk      Bulk record attendance
GET/POST  /api/v1/fees/                List / Create fees
POST      /api/v1/fees/{id}/pay        Record payment
GET/POST  /api/v1/announcements/       List / Post announcements
GET       /api/v1/notifications/       List notifications
PUT       /api/v1/notifications/read-all    Mark all as read
GET       /api/v1/admin/dashboard      Admin dashboard statistics
```

---

## 🛠️ Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Backend Framework** | FastAPI | 0.111 |
| **Database** | PostgreSQL | 14+ |
| **ORM** | SQLAlchemy | 2.0 |
| **Authentication** | python-jose (JWT) + passlib (bcrypt) | — |
| **Data Validation** | Pydantic | v2 |
| **Templating** | Jinja2 | 3.1 |
| **Frontend** | HTML5 + CSS3 + Vanilla JavaScript | — |
| **Charts** | Chart.js | 4.4 |
| **Typography** | Google Fonts — Syne + DM Sans | — |
| **ASGI Server** | Uvicorn | 0.29 |

---

## 🚀 Production Deployment

### Gunicorn *(Linux / macOS)*
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install bcrypt==4.0.1
COPY . .
RUN mkdir -p app/static uploads
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

```bash
docker build -t educore .
docker run -p 8000:8000 --env-file .env educore
```

### Generate a Secure SECRET_KEY
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🐛 Troubleshooting

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'app'` | Run as `python -m scripts.seed` not `python scripts/seed.py` |
| `bcrypt version error / password longer than 72 bytes` | `pip install bcrypt==4.0.1` |
| `Directory 'app/static' does not exist` | `mkdir app\static` (Windows) or `mkdir -p app/static` (Mac/Linux) |
| `psql not recognized` | Add PostgreSQL bin to PATH: `C:\Program Files\PostgreSQL\16\bin` |
| `.env.example not found` | Create `.env` manually using the template in step 4 above |
| `No module named 'sqlalchemy'` | Run `pip install -r requirements.txt` inside your activated venv |

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. **Fork** the repository
2. **Create** a feature branch — `git checkout -b feature/my-feature`
3. **Commit** your changes — `git commit -m 'Add my feature'`
4. **Push** to the branch — `git push origin feature/my-feature`
5. **Open** a Pull Request

### Roadmap
- [ ] Email notifications via SMTP
- [ ] PDF report export for grades and attendance
- [ ] CSV data export for all tables
- [ ] Student photo upload
- [ ] Parent portal role
- [ ] Dark mode toggle
- [ ] Visual timetable grid
- [ ] Multi-school / multi-tenant support
- [ ] React Native mobile app

---

## 📄 License

This project is licensed under the **MIT License** — free to use, modify, and distribute.

---

## 👨‍💻 Author

**Built by v44heat**

> EduCore was designed and developed as a complete full-stack school management solution, implementing production-grade patterns including JWT authentication, role-based access control, a fully normalized 15-table PostgreSQL schema, 40+ REST API endpoints, and a modern responsive single-page dashboard.

---

<div align="center">

**⭐ If this project helped you, please give it a star!**


</div>
