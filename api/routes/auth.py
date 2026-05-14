from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any
from api.dependencies import get_db
from core.security import verify_password, create_access_token
from db.models import User
from schemas.user import Token

router = APIRouter()

@router.post("/login", response_model=Token)
def login_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    permissions = []
    if user.role:
        permissions = [p.name for p in user.role.permissions]
        
    access_token = create_access_token(
        subject=user.id, permissions=permissions
    )
    return {"access_token": access_token, "token_type": "bearer"}
