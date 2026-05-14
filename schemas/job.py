from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class JobBase(BaseModel):
    title: str
    client_name: Optional[str] = None
    experience_range: Optional[str] = None
    location: Optional[str] = None
    work_mode: Optional[str] = None
    budget: Optional[str] = None
    number_of_positions: Optional[int] = 1
    description: Optional[str] = None
    status: Optional[str] = "Open"

class JobCreate(JobBase):
    skills_required: Optional[List[str]] = []

class JobOut(JobBase):
    id: int
    created_at: datetime
    created_by: Optional[int] = None
    skills_required: Optional[List[str]] = []

    class Config:
        from_attributes = True
