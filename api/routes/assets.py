from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from api.dependencies import get_db, get_current_user
from db.models import Asset, Employee, User
from pydantic import BaseModel
from datetime import date

router = APIRouter(prefix="/assets", tags=["assets"])

class AssetOut(BaseModel):
    id: int
    name: str
    asset_type: str
    serial_number: Optional[str]
    status: str
    assigned_employee_name: Optional[str]
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[AssetOut])
def get_assets(db: Session = Depends(get_db)):
    assets = db.query(Asset).all()
    result = []
    for a in assets:
        result.append({
            "id": a.id,
            "name": a.name,
            "asset_type": a.asset_type,
            "serial_number": a.serial_number,
            "status": a.status,
            "assigned_employee_name": a.assigned_employee.user.name if a.assigned_employee else None
        })
    return result

@router.post("/")
def create_asset(name: str, asset_type: str, serial_number: str, db: Session = Depends(get_db)):
    asset = Asset(name=name, asset_type=asset_type, serial_number=serial_number)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset
