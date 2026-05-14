from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    mobile: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role_id: Optional[int] = None

class UserOut(UserBase):
    id: int
    role_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None
    permissions: List[str] = []
