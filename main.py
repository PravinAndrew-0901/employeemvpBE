from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.routes import auth, roles, candidates, jobs, dashboard, follow_ups, reports, users, settings as settings_router, applications
from db.database import engine, Base
from fastapi.staticfiles import StaticFiles
import os

# Create tables if they don't exist, though typically handled by Alembic or seed script
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="HR Recruiter MVP API",
    version="1.0.0"
)

# Static files for CV uploads
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For MVP. In production, restrict this.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/")
def read_root():
    return {"message": "Welcome to the HR Recruiter API"}
