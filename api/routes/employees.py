from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from api.dependencies import get_db, check_permission
from db.models import Employee, User, Candidate, CandidateStatus, EmployeeStatus
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/employees", tags=["employees"])

class EmployeeOut(BaseModel):
    id: int
    employee_code: str
    full_name: str
    email: str
    department_name: Optional[str]
    designation_title: Optional[str]
    status: str
    joining_date: datetime
    
    class Config:
        from_attributes = True

class HireRequest(BaseModel):
    candidate_id: int
    employee_code: str
    department_id: int
    designation_id: int
    base_salary: float
    joining_date: datetime

@router.get("/", response_model=List[EmployeeOut])
def get_employees(db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
    result = []
    for emp in employees:
        result.append({
            "id": emp.id,
            "employee_code": emp.employee_code,
            "full_name": emp.user.name,
            "email": emp.user.email,
            "department_name": emp.department.name if emp.department else None,
            "designation_title": emp.designation.title if emp.designation else None,
            "status": emp.status,
            "joining_date": emp.joining_date
        })
    return result

@router.post("/hire", status_code=status.HTTP_201_CREATED)
def hire_candidate(
    req: HireRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("manage_users"))
):
    """Transition a candidate to an employee"""
    candidate = db.query(Candidate).filter(Candidate.id == req.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    if candidate.status == CandidateStatus.JOINED:
        raise HTTPException(status_code=400, detail="Candidate already joined")
        
    # Find or create user for the employee
    user = db.query(User).filter(User.email == candidate.email).first()
    if not user:
        # Should normally have a user if they registered, but let's be safe
        user = User(
            name=candidate.full_name,
            email=candidate.email,
            password_hash="placeholder", # Should be changed by employee on first login
            is_employee=True
        )
        db.add(user)
        db.flush()
    else:
        user.is_employee = True
    
    # Create employee record
    employee = Employee(
        user_id=user.id,
        candidate_id=candidate.id,
        employee_code=req.employee_code,
        department_id=req.department_id,
        designation_id=req.designation_id,
        base_salary=req.base_salary,
        joining_date=req.joining_date,
        status=EmployeeStatus.PROBATION
    )
    db.add(employee)
    
    # Update candidate status
    candidate.status = CandidateStatus.JOINED
    
    db.commit()
    return {"message": f"Successfully hired {candidate.full_name}", "employee_id": employee.id}
