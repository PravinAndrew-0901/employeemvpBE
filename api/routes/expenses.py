from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from api.dependencies import get_db, get_current_user
from db.models import Expense, Employee, User
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/expenses", tags=["expenses"])

class ExpenseOut(BaseModel):
    id: int
    employee_name: str
    title: str
    amount: float
    category: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[ExpenseOut])
def get_all_expenses(db: Session = Depends(get_db)):
    expenses = db.query(Expense).all()
    result = []
    for e in expenses:
        result.append({
            "id": e.id,
            "employee_name": e.employee.user.name,
            "title": e.title,
            "amount": e.amount,
            "category": e.category,
            "status": e.status,
            "created_at": e.created_at
        })
    return result

@router.post("/")
def claim_expense(title: str, amount: float, category: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not emp:
        raise HTTPException(status_code=403, detail="Only employees can claim expenses")
        
    expense = Expense(
        employee_id=emp.id,
        title=title,
        amount=amount,
        category=category
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense
