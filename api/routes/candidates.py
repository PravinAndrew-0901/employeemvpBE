from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Any, Optional
from api.dependencies import get_db, check_permission, get_current_user
from db.models import Candidate, User
from schemas.candidate import CandidateOut, CandidateCreate, CandidatePaginated
from services.candidate_svc import create_candidate, bulk_upload_cvs

router = APIRouter()

from db.models import Role
from core.security import get_password_hash

@router.post("/register", response_model=CandidateOut, status_code=status.HTTP_201_CREATED)
async def register_candidate(
    full_name: str = Form(...),
    email: str = Form(...),
    mobile: str = Form(...),
    password: Optional[str] = Form(None),
    current_location: Optional[str] = Form(None),
    total_experience: Optional[float] = Form(None),
    cv_file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a candidate with a single CV upload (Public Route)
    """
    if cv_file.content_type != "application/pdf":
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Invalid file type. Only PDF allowed.")
        
    candidate_in = CandidateCreate(
        full_name=full_name,
        email=email,
        mobile=mobile,
        current_location=current_location,
        total_experience=total_experience
    )
    
    duplicate = db.query(Candidate).filter(
        (Candidate.email == email) | (Candidate.mobile == mobile)
    ).first()
    
    if duplicate:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Candidate with this email or mobile already exists")
    
    # Create Candidate User
    user_id = None
    if password:
        user_dup = db.query(User).filter(User.email == email).first()
        if not user_dup:
            candidate_role = db.query(Role).filter(Role.name == "Candidate").first()
            if not candidate_role:
                candidate_role = Role(name="Candidate", description="Candidate User", is_system_role=True)
                db.add(candidate_role)
                db.commit()
            
            new_user = User(
                email=email,
                name=full_name,
                password_hash=get_password_hash(password),
                role_id=candidate_role.id
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            user_id = new_user.id
    
    candidate = await create_candidate(db, candidate_in, cv_file, user_id)
    return candidate

@router.post("/bulk-upload", status_code=status.HTTP_207_MULTI_STATUS)
async def bulk_upload(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("bulk_upload_cv"))
) -> Any:
    """
    Bulk upload CVs.
    """
    results = await bulk_upload_cvs(db, files, current_user.id)
    return {"results": results}

@router.get("/", response_model=CandidatePaginated)
def get_candidates(
    skills: Optional[str] = None,
    experience: Optional[str] = None, # format: "2-5"
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("view_candidates"))
) -> Any:
    if page < 1 or size < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid pagination parameters")
        
    query = db.query(Candidate)
    
    # Filter by skills (basic text matching for JSON if text-based, or simpler)
    # Filter by experience
    
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    
    return CandidatePaginated(total=total, page=page, size=size, items=items)

from pydantic import BaseModel

class StatusUpdate(BaseModel):
    status: str

@router.get("/{candidate_id}", response_model=CandidateOut)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("view_candidates"))
) -> Any:
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@router.put("/{candidate_id}/status", response_model=CandidateOut)
def update_candidate_status(
    candidate_id: int,
    status_update: StatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    try:
        from db.models import CandidateStatus
        candidate.status = CandidateStatus(status_update.status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status value")
        
    db.commit()
    db.refresh(candidate)
    return candidate
