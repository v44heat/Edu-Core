from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

from app.core.config import settings
from app.core.database import Base, engine
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.academics import (
    students_router, teachers_router, classes_router, subjects_router
)
from app.api.operations import (
    assignments_router, submissions_router, grades_router,
    attendance_router, announcements_router, fees_router,
    timetable_router, notifications_router, admin_router
)

# Create tables
Base.metadata.create_all(bind=engine)

# Create upload directories
os.makedirs("uploads/assignments", exist_ok=True)
os.makedirs("uploads/submissions", exist_ok=True)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Comprehensive School Management System API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files & templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# API Routes
api_prefix = "/api/v1"
app.include_router(auth_router, prefix=api_prefix)
app.include_router(users_router, prefix=api_prefix)
app.include_router(students_router, prefix=api_prefix)
app.include_router(teachers_router, prefix=api_prefix)
app.include_router(classes_router, prefix=api_prefix)
app.include_router(subjects_router, prefix=api_prefix)
app.include_router(assignments_router, prefix=api_prefix)
app.include_router(submissions_router, prefix=api_prefix)
app.include_router(grades_router, prefix=api_prefix)
app.include_router(attendance_router, prefix=api_prefix)
app.include_router(announcements_router, prefix=api_prefix)
app.include_router(fees_router, prefix=api_prefix)
app.include_router(timetable_router, prefix=api_prefix)
app.include_router(notifications_router, prefix=api_prefix)
app.include_router(admin_router, prefix=api_prefix)


# Frontend Routes
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/students", response_class=HTMLResponse)
async def students_page(request: Request):
    return templates.TemplateResponse("students.html", {"request": request})


@app.get("/teachers", response_class=HTMLResponse)
async def teachers_page(request: Request):
    return templates.TemplateResponse("teachers.html", {"request": request})


@app.get("/classes", response_class=HTMLResponse)
async def classes_page(request: Request):
    return templates.TemplateResponse("classes.html", {"request": request})


@app.get("/assignments", response_class=HTMLResponse)
async def assignments_page(request: Request):
    return templates.TemplateResponse("assignments.html", {"request": request})


@app.get("/grades", response_class=HTMLResponse)
async def grades_page(request: Request):
    return templates.TemplateResponse("grades.html", {"request": request})


@app.get("/attendance", response_class=HTMLResponse)
async def attendance_page(request: Request):
    return templates.TemplateResponse("attendance.html", {"request": request})


@app.get("/fees", response_class=HTMLResponse)
async def fees_page(request: Request):
    return templates.TemplateResponse("fees.html", {"request": request})


@app.get("/announcements", response_class=HTMLResponse)
async def announcements_page(request: Request):
    return templates.TemplateResponse("announcements.html", {"request": request})
