from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from api.dependencies import get_db, get_current_user
from db.models import Employee, Attendance, User
from pydantic import BaseModel
from datetime import datetime, date as date_type

router = APIRouter(prefix="/attendance", tags=["attendance"])

class AttendanceOut(BaseModel):
    id: int
    employee_name: str
    date: date_type
    check_in: datetime
    check_out: Optional[datetime]
    status: str
    work_location: Optional[str]
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[AttendanceOut])
def get_all_attendance(db: Session = Depends(get_db)):
    records = db.query(Attendance).all()
    result = []
    for r in records:
        result.append({
            "id": r.id,
            "employee_name": r.employee.user.name,
            "date": r.date,
            "check_in": r.check_in,
            "check_out": r.check_out,
            "status": r.status,
            "work_location": r.work_location
        })
    return result

@router.post("/check-in")
def check_in(work_location: str = "Office", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not emp:
        raise HTTPException(status_code=403, detail="Only employees can check in")
        
    # Check if already checked in today
    today = date_type.today()
    existing = db.query(Attendance).filter(Attendance.employee_id == emp.id, Attendance.date == today).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already checked in for today")
        
    record = Attendance(
        employee_id=emp.id,
        date=today,
        work_location=work_location,
        status="Present"
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@router.post("/check-out")
def check_out(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not emp:
        raise HTTPException(status_code=403, detail="Only employees can check out")
        
    today = date_type.today()
    record = db.query(Attendance).filter(Attendance.employee_id == emp.id, Attendance.date == today).first()
    if not record:
        raise HTTPException(status_code=404, detail="No check-in record found for today")
    
    if record.check_out:
        raise HTTPException(status_code=400, detail="Already checked out")
        
    record.check_out = datetime.now()
    db.commit()
    db.refresh(record)
    return record
