from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any
from api.dependencies import get_db, get_current_user
from db.models import Job, Candidate, JobApplication, User, CandidateStatus
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/applications", tags=["applications"])

class ApplicationOut(BaseModel):
    id: int
    job_id: int
    job_title: str
    status: str
    applied_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/apply/{job_id}", status_code=status.HTTP_201_CREATED)
def apply_for_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if user is a candidate
    candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
    if not candidate:
        raise HTTPException(status_code=403, detail="Only candidates can apply for jobs")
    
    # Check if job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if already applied
    existing = db.query(JobApplication).filter(
        JobApplication.job_id == job_id,
        JobApplication.candidate_id == candidate.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already applied for this job")
    
    application = JobApplication(
        job_id=job_id,
        candidate_id=candidate.id,
        status=CandidateStatus.NEW
    )
    db.add(application)
    db.commit()
    return {"message": "Application submitted successfully"}

@router.get("/my-applications", response_model=List[ApplicationOut])
def get_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
    if not candidate:
        return []
    
    apps = db.query(JobApplication).filter(JobApplication.candidate_id == candidate.id).all()
    
    result = []
    for app in apps:
        result.append({
            "id": app.id,
            "job_id": app.job_id,
            "job_title": app.job.title,
            "status": app.status,
            "applied_at": app.applied_at
        })
    return result
