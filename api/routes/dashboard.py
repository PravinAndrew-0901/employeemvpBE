from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Any, Dict
from api.dependencies import get_db, check_permission
from db.models import Candidate, CandidateStatus, User

router = APIRouter()

@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("view_candidates"))
) -> Any:
    """
    Get dashboard summary statistics as per SRS 3.12
    """
    total_candidates = db.query(Candidate).count()
    
    # Status counts
    status_counts = db.query(Candidate.status, func.count(Candidate.id)).group_by(Candidate.status).all()
    status_dict = {status.value: count for status, count in status_counts}
    
    # Recruiter-wise count
    recruiter_counts = db.query(User.name, func.count(Candidate.id))\
        .join(Candidate, User.id == Candidate.assigned_recruiter_id)\
        .group_by(User.name).all()
    
    recruiter_dict = {name: count for name, count in recruiter_counts}
    
    return {
        "total_candidates": total_candidates,
        "new_cvs": status_dict.get(CandidateStatus.NEW.value, 0),
        "shortlisted": status_dict.get(CandidateStatus.SHORTLISTED.value, 0),
        "rejected": status_dict.get(CandidateStatus.REJECTED.value, 0),
        "interview_scheduled": status_dict.get(CandidateStatus.INTERVIEW_SCHEDULED.value, 0),
        "selected": status_dict.get(CandidateStatus.SELECTED.value, 0),
        "joined": status_dict.get(CandidateStatus.JOINED.value, 0),
        "status_distribution": status_dict,
        "recruiter_distribution": recruiter_dict
    }
