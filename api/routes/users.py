from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any
from api.dependencies import get_db, check_permission
from db.models import User, Role
from schemas.user import UserCreate, UserOut
from core.security import get_password_hash

router = APIRouter()

@router.get("/", response_model=List[UserOut])
def get_users(
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("manage_users"))
) -> Any:
    """Get all internal users"""
    return db.query(User).filter(User.is_candidate == False).all()

@router.post("/", response_model=UserOut)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("manage_users"))
) -> Any:
    """Create a new internal user and assign a role"""
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        mobile=user_in.mobile,
        password_hash=get_password_hash(user_in.password),
        role_id=user_in.role_id,
        is_candidate=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_in: UserCreate, # Reusing UserCreate for simplicity in MVP
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("manage_users"))
) -> Any:
    """Update user details and role"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.name = user_in.name
    user.mobile = user_in.mobile
    if user_in.password:
        user.password_hash = get_password_hash(user_in.password)
    user.role_id = user_in.role_id
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("manage_users"))
) -> Any:
    """Delete a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
