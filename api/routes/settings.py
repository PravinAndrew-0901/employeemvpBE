from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from api.dependencies import get_db, get_current_user, check_permission
from db.models import Skill, FilterOption
from pydantic import BaseModel

router = APIRouter(prefix="/settings", tags=["settings"])

# --- Schemas ---
class SkillBase(BaseModel):
    name: str
    category: Optional[str] = None
    is_active: bool = True

class SkillCreate(SkillBase):
    pass

class SkillResponse(SkillBase):
    id: int
    class Config:
        from_attributes = True

class FilterOptionBase(BaseModel):
    category: str
    value: str
    label: Optional[str] = None
    sort_order: int = 0

class FilterOptionCreate(FilterOptionBase):
    pass

class FilterOptionResponse(FilterOptionBase):
    id: int
    class Config:
        from_attributes = True

# --- Skill Routes ---

@router.get("/skills", response_model=List[SkillResponse])
def get_skills(db: Session = Depends(get_db)):
    return db.query(Skill).filter(Skill.is_active == True).all()

@router.post("/skills", response_model=SkillResponse)
def create_skill(
    skill: SkillCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("manage_settings"))
):
    db_skill = Skill(**skill.dict())
    db.add(db_skill)
    try:
        db.commit()
        db.refresh(db_skill)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Skill already exists")
    return db_skill

@router.delete("/skills/{skill_id}")
def delete_skill(
    skill_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("manage_settings"))
):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    db.delete(skill)
    db.commit()
    return {"message": "Skill deleted"}

# --- Filter Option Routes ---

@router.get("/filters/{category}", response_model=List[FilterOptionResponse])
def get_filter_options(category: str, db: Session = Depends(get_db)):
    return db.query(FilterOption).filter(FilterOption.category == category).order_by(FilterOption.sort_order).all()

@router.get("/filters", response_model=List[FilterOptionResponse])
def get_all_filter_options(db: Session = Depends(get_db)):
    return db.query(FilterOption).order_by(FilterOption.category, FilterOption.sort_order).all()

@router.post("/filters", response_model=FilterOptionResponse)
def create_filter_option(
    option: FilterOptionCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("manage_settings"))
):
    db_option = FilterOption(**option.dict())
    db.add(db_option)
    db.commit()
    db.refresh(db_option)
    return db_option

@router.delete("/filters/{option_id}")
def delete_filter_option(
    option_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("manage_settings"))
):
    option = db.query(FilterOption).filter(FilterOption.id == option_id).first()
    if not option:
        raise HTTPException(status_code=404, detail="Option not found")
    db.delete(option)
    db.commit()
    return {"message": "Option deleted"}
