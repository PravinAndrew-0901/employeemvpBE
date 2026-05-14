from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from db.models import CandidateStatus

class CandidateBase(BaseModel):
    full_name: str
    email: EmailStr
    mobile: str
    alternate_mobile: Optional[str] = None
    current_location: Optional[str] = None
    preferred_location: Optional[str] = None
    total_experience: Optional[float] = None
    relevant_experience: Optional[float] = None
    current_company: Optional[str] = None
    current_designation: Optional[str] = None
    current_ctc: Optional[str] = None
    expected_ctc: Optional[str] = None
    notice_period: Optional[str] = None
    source: Optional[str] = None
    applied_role: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    remarks: Optional[str] = None
    status: Optional[CandidateStatus] = CandidateStatus.NEW
    assigned_recruiter_id: Optional[int] = None

class CandidateCreate(CandidateBase):
    skills: Optional[List[str]] = []

class CandidateUpdate(CandidateBase):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    skills: Optional[List[str]] = None

class CandidateOut(CandidateBase):
    id: int
    status: CandidateStatus
    is_duplicate: bool
    created_at: datetime
    updated_at: datetime
    cv_file_path: Optional[str] = None
    skills: Optional[Any] = None
    
    class Config:
        from_attributes = True

class CandidatePaginated(BaseModel):
    total: int
    page: int
    size: int
    items: List[CandidateOut]
