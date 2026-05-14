from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from api.dependencies import get_db, get_current_user
from db.models import Employee, SupportTicket, TicketComment, User, TicketStatus, TicketPriority
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/tickets", tags=["tickets"])

class TicketOut(BaseModel):
    id: int
    title: str
    priority: str
    status: str
    category: Optional[str]
    created_by_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class TicketCreate(BaseModel):
    title: str
    description: str
    priority: TicketPriority = TicketPriority.MEDIUM
    category: str

@router.get("/", response_model=List[TicketOut])
def get_tickets(db: Session = Depends(get_db)):
    tickets = db.query(SupportTicket).all()
    result = []
    for t in tickets:
        result.append({
            "id": t.id,
            "title": t.title,
            "priority": t.priority,
            "status": t.status,
            "category": t.category,
            "created_by_name": t.creator.user.name if t.creator else "Unknown",
            "created_at": t.created_at
        })
    return result

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_ticket(req: TicketCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not emp:
        raise HTTPException(status_code=403, detail="Only employees can create tickets")
        
    ticket = SupportTicket(
        title=req.title,
        description=req.description,
        priority=req.priority,
        category=req.category,
        created_by_id=emp.id,
        status=TicketStatus.OPEN
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket
