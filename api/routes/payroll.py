from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from api.dependencies import get_db, check_permission
from db.models import Employee, PaySlip, User
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/payroll", tags=["payroll"])

class PaySlipOut(BaseModel):
    id: int
    employee_name: str
    month: int
    year: int
    net_salary: float
    status: str
    generated_at: datetime
    
    class Config:
        from_attributes = True

class GeneratePaySlipRequest(BaseModel):
    employee_id: int
    month: int
    year: int
    allowances: dict = {}
    deductions: dict = {}

@router.get("/slips", response_model=List[PaySlipOut])
def get_all_slips(db: Session = Depends(get_db), current_user: User = Depends(check_permission("manage_users"))):
    slips = db.query(PaySlip).all()
    result = []
    for s in slips:
        result.append({
            "id": s.id,
            "employee_name": s.employee.user.name,
            "month": s.month,
            "year": s.year,
            "net_salary": s.net_salary,
            "status": s.status,
            "generated_at": s.generated_at
        })
    return result

@router.post("/generate", status_code=status.HTTP_201_CREATED)
def generate_slip(req: GeneratePaySlipRequest, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == req.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    total_allowance = sum(req.allowances.values())
    total_deduction = sum(req.deductions.values())
    net_salary = emp.base_salary + total_allowance - total_deduction
    
    slip = PaySlip(
        employee_id=emp.id,
        month=req.month,
        year=req.year,
        basic_salary=emp.base_salary,
        allowances=req.allowances,
        deductions=req.deductions,
        net_salary=net_salary,
        status='Generated'
    )
    db.add(slip)
    db.commit()
    db.refresh(slip)
    return slip
