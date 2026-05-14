from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.routes import (
    auth, roles, candidates, jobs, dashboard, 
    follow_ups, reports, users, settings as settings_router, 
    applications, employees, payroll, leaves, tickets,
    attendance, announcements, assets, expenses
)
from db.database import engine, Base
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Corporate HRMS & Recruiter API",
    version="1.0.0"
)

# Static files for CV uploads
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routes Registration ---
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(roles.router, prefix="/api/roles", tags=["roles"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["candidates"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(follow_ups.router, prefix="/api/follow-ups", tags=["follow-ups"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(settings_router.router, prefix="/api", tags=["settings"])
app.include_router(applications.router, prefix="/api", tags=["applications"])

# HRMS & Enterprise Modules
app.include_router(employees.router, prefix="/api", tags=["employees"])
app.include_router(payroll.router, prefix="/api", tags=["payroll"])
app.include_router(leaves.router, prefix="/api", tags=["leaves"])
app.include_router(tickets.router, prefix="/api", tags=["tickets"])
app.include_router(attendance.router, prefix="/api", tags=["attendance"])
app.include_router(announcements.router, prefix="/api", tags=["announcements"])
app.include_router(assets.router, prefix="/api", tags=["assets"])
app.include_router(expenses.router, prefix="/api", tags=["expenses"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Corporate HRMS & Recruiter API"}
