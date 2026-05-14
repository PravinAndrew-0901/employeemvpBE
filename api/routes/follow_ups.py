from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any
from api.dependencies import get_db, check_permission, get_current_user
from db.models import FollowUp, Candidate, User
from schemas.follow_up import FollowUpCreate, FollowUpOut

router = APIRouter()

@router.post("/", response_model=FollowUpOut, status_code=status.HTTP_201_CREATED)
def create_follow_up(
    follow_up_in: FollowUpCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # Ensure candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == follow_up_in.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    follow_up = FollowUp(
        candidate_id=follow_up_in.candidate_id,
        next_follow_up_date=follow_up_in.next_follow_up_date,
        type=follow_up_in.type,
        remarks=follow_up_in.remarks,
        updated_by=current_user.id
    )
    db.add(follow_up)
    db.commit()
    db.refresh(follow_up)
    return follow_up

@router.get("/candidate/{candidate_id}", response_model=List[FollowUpOut])
def get_candidate_follow_ups(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    return db.query(FollowUp).filter(FollowUp.candidate_id == candidate_id).order_by(FollowUp.follow_up_date.desc()).all()
