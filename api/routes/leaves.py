from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from api.dependencies import get_db, get_current_user
from db.models import Employee, LeaveRequest, LeaveBalance, User, LeaveStatus, LeaveType
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/leaves", tags=["leaves"])

class LeaveRequestOut(BaseModel):
    id: int
    employee_name: str
    leave_type: str
    start_date: datetime
    end_date: datetime
    status: str
    reason: Optional[str]
    
    class Config:
        from_attributes = True

class LeaveRequestCreate(BaseModel):
    leave_type: LeaveType
    start_date: datetime
    end_date: datetime
    reason: str

@router.get("/requests", response_model=List[LeaveRequestOut])
def get_all_leave_requests(db: Session = Depends(get_db)):
    requests = db.query(LeaveRequest).all()
    result = []
    for r in requests:
        result.append({
            "id": r.id,
            "employee_name": r.employee.user.name,
            "leave_type": r.leave_type,
            "start_date": r.start_date,
            "end_date": r.end_date,
            "status": r.status,
            "reason": r.reason
        })
    return result

@router.post("/apply", status_code=status.HTTP_201_CREATED)
def apply_leave(req: LeaveRequestCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not emp:
        raise HTTPException(status_code=403, detail="Only employees can apply for leave")
        
    leave_req = LeaveRequest(
        employee_id=emp.id,
        leave_type=req.leave_type,
        start_date=req.start_date,
        end_date=req.end_date,
        reason=req.reason,
        status=LeaveStatus.PENDING
    )
    db.add(leave_req)
    db.commit()
    return {"message": "Leave request submitted"}
