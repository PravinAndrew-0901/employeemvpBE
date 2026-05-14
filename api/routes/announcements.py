from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from api.dependencies import get_db, get_current_user
from db.models import Announcement, User
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/announcements", tags=["announcements"])

class AnnouncementOut(BaseModel):
    id: int
    title: str
    content: str
    priority: str
    created_at: datetime
    creator_name: str
    
    class Config:
        from_attributes = True

class AnnouncementCreate(BaseModel):
    title: str
    content: str
    priority: str = "Medium"

@router.get("/", response_model=List[AnnouncementOut])
def get_active_announcements(db: Session = Depends(get_db)):
    announcements = db.query(Announcement).filter(Announcement.is_active == True).order_by(Announcement.created_at.desc()).all()
    result = []
    for a in announcements:
        result.append({
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "priority": a.priority,
            "created_at": a.created_at,
            "creator_name": a.creator.name if a.creator else "System"
        })
    return result

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_announcement(req: AnnouncementCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    announcement = Announcement(
        title=req.title,
        content=req.content,
        priority=req.priority,
        created_by_id=current_user.id
    )
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement
