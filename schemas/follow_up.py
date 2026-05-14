from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from db.models import FollowUpType

class FollowUpBase(BaseModel):
    candidate_id: int
    next_follow_up_date: Optional[datetime] = None
    type: FollowUpType
    remarks: Optional[str] = None

class FollowUpCreate(FollowUpBase):
    pass

class FollowUpOut(FollowUpBase):
    id: int
    follow_up_date: datetime
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True
