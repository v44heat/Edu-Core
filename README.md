# 🎓 EduCore — School Management System

A production-ready, full-stack School Management System built with **FastAPI**, **PostgreSQL**, and a modern responsive UI.

---

## 📸 System Overview

| Role | Username | Password |
|------|----------|----------|
| Super Admin | `superadmin` | `Admin@1234` |
| Admin | `admin` | `Admin@1234` |
| Teacher | `john.doe` | `Teacher@1234` |
| Student | `alice` | `Student@1234` |

---

## 🏗️ Project Structure

```
school_mgmt/
├── main.py                     # FastAPI app entry point
├── requirements.txt
├── schema.sql                  # Full PostgreSQL schema
├── .env.example                # Environment variables template
│
├── app/
│   ├── api/
│   │   ├── auth.py             # Login, logout, token refresh
│   │   ├── users.py            # User CRUD
│   │   ├── academics.py        # Students, teachers, classes, subjects
│   │   ├── operations.py       # Assignments, grades, attendance, fees, etc.
│   │   └── deps.py             # Auth dependencies & RBAC
│   ├── core/
│   │   ├── config.py           # Settings from .env
│   │   ├── database.py         # SQLAlchemy engine & session
│   │   └── security.py         # JWT, bcrypt utilities
│   ├── models/
│   │   └── models.py           # All SQLAlchemy ORM models
│   ├── schemas/
│   │   └── schemas.py          # Pydantic request/response schemas
│   ├── templates/
│   │   ├── login.html          # Login page
│   │   └── dashboard.html      # Main SPA dashboard
│   └── static/                 # CSS, JS, images
│
└── scripts/
    └── seed.py                 # Database seed data
```

---

## ⚡ Quick Start

### 1. Prerequisites

- Python 3.10+
- PostgreSQL 14+
- `pip`

### 2. Clone & Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env
# Edit .env with your database credentials
```

### 3. Setup Database

```bash
# Create the database
psql -U postgres -c "CREATE DATABASE school_mgmt;"

# Optional: Run schema manually
psql -U postgres -d school_mgmt -f schema.sql

# Or let SQLAlchemy auto-create tables (happens on first run)
```

### 4. Seed Sample Data

```bash
python scripts/seed.py
```

### 5. Run the Server

```bash
uvicorn main:app --reload --port 8000
```

### 6. Access the System

| URL | Description |
|-----|-------------|
| http://localhost:8000 | Login page |
| http://localhost:8000/dashboard | Main dashboard |
| http://localhost:8000/api/docs | Swagger API docs |
| http://localhost:8000/api/redoc | ReDoc API docs |

---

## 🔑 Authentication

- **JWT Bearer tokens** (access + refresh)
- **bcrypt** password hashing
- **Role-based access control** (RBAC) with 4 roles

### Token Flow
```
POST /api/v1/auth/login     → { access_token, refresh_token, user }
POST /api/v1/auth/refresh   → new tokens
POST /api/v1/auth/logout    → invalidates session
GET  /api/v1/auth/me        → current user info
```

---

## 🌐 API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/auth/refresh` | Refresh token |
| POST | `/api/v1/auth/logout` | Logout |
| GET | `/api/v1/auth/me` | Current user |
| POST | `/api/v1/auth/change-password` | Change password |

### Users (Admin+)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/` | List users |
| POST | `/api/v1/users/` | Create user |
| GET | `/api/v1/users/{id}` | Get user |
| PUT | `/api/v1/users/{id}` | Update user |
| DELETE | `/api/v1/users/{id}` | Delete user (Super Admin) |
| GET | `/api/v1/users/stats/overview` | User statistics |

### Students
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/students/` | List students |
| POST | `/api/v1/students/` | Create student profile |
| GET | `/api/v1/students/{id}` | Get student |
| GET | `/api/v1/students/{id}/dashboard` | Student dashboard data |

### Teachers / Classes / Subjects
Similar CRUD endpoints at `/api/v1/teachers/`, `/api/v1/classes/`, `/api/v1/subjects/`

### Assignments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/assignments/` | List assignments |
| POST | `/api/v1/assignments/` | Create assignment |
| POST | `/api/v1/assignments/{id}/upload` | Upload file |

### Grades
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/grades/` | List grades |
| POST | `/api/v1/grades/` | Record grade |
| GET | `/api/v1/grades/analytics/{class_id}` | Grade analytics |

### Attendance
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/attendance/` | List records |
| POST | `/api/v1/attendance/bulk` | Bulk record |

### Fees
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/fees/` | List fees |
| POST | `/api/v1/fees/` | Create fee |
| POST | `/api/v1/fees/{id}/pay` | Record payment |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/dashboard` | Admin dashboard stats |

---

## 🛡️ Security Features

- ✅ JWT access tokens (60 min) + refresh tokens (7 days)
- ✅ bcrypt password hashing (cost factor 12)
- ✅ Role-based access control (4 roles)
- ✅ SQL injection protection via SQLAlchemy ORM
- ✅ Input validation via Pydantic
- ✅ Activity logging for all actions
- ✅ CORS configuration

---

## 🗃️ Database Schema

### Key Tables
| Table | Purpose |
|-------|---------|
| `users` | Authentication & base info |
| `students` | Student profiles |
| `teachers` | Teacher profiles |
| `classes` | School classes/sections |
| `subjects` | Academic subjects |
| `subject_assignments` | Teacher ↔ Subject ↔ Class mapping |
| `enrollments` | Student ↔ Subject enrollment |
| `assignments` | Homework/assignments |
| `submissions` | Student submissions |
| `grades` | Exam/quiz grades |
| `attendance` | Daily attendance |
| `fees` | School fees tracking |
| `announcements` | School announcements |
| `notifications` | User notifications |
| `activity_logs` | System audit trail |

---

## 🎨 UI Features

- **Responsive sidebar** dashboard (works on mobile)
- **Role-aware navigation** (menus adapt to user role)
- **Data tables** with search/filter
- **Charts** for attendance & grade distribution (Chart.js)
- **Modal forms** for CRUD operations
- **Toast notifications** for feedback
- **Live stats** cards on dashboard
- **Quick demo login** buttons on login page

---

## 🔧 Environment Variables

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/school_mgmt
SECRET_KEY=your-super-secret-key-minimum-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
UPLOAD_DIR=uploads
```

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI 0.111 |
| Database | PostgreSQL 14+ |
| ORM | SQLAlchemy 2.0 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Validation | Pydantic v2 |
| Frontend | HTML5 + CSS3 + Vanilla JS |
| Charts | Chart.js 4.4 |
| Fonts | Google Fonts (Syne + DM Sans) |
| Server | Uvicorn (ASGI) |

---

## 🚀 Production Deployment

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or with Docker
docker build -t educore .
docker run -p 8000:8000 --env-file .env educore
```

---

## 📝 License

MIT License — Free to use and modify for educational purposes.
