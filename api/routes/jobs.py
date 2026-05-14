from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any
from api.dependencies import get_db, check_permission, get_current_user
from db.models import Job, User
from schemas.job import JobCreate, JobOut

router = APIRouter()

@router.post("/", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(
    job_in: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("manage_roles")) 
) -> Any:
    job = Job(**job_in.dict(), created_by=current_user.id)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.get("/", response_model=List[JobOut])
def get_jobs_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("view_candidates"))
) -> Any:
    return db.query(Job).all()

@router.get("/public", response_model=List[JobOut])
def get_public_jobs(
    db: Session = Depends(get_db)
) -> Any:
    """Public list of jobs for candidates"""
    return db.query(Job).filter(Job.status == 'Open').all()

@router.get("/{job_id}", response_model=JobOut)
def get_job_detail(
    job_id: int,
    db: Session = Depends(get_db)
) -> Any:
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
