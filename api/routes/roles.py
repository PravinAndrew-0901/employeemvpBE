from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any
from api.dependencies import get_db, check_permission
from db.models import Role, Permission, RolePermission
from schemas.role import RoleCreate, RoleOut

router = APIRouter()

@router.post("/", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
def create_role(
    role_in: RoleCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("manage_roles"))
) -> Any:
    """
    Create new role.
    """
    role = db.query(Role).filter(Role.name == role_in.name).first()
    if role:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The role with this name already exists in the system.",
        )
    
    new_role = Role(name=role_in.name, description=role_in.description)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    # Add permissions
    if role_in.permission_ids:
        for perm_id in role_in.permission_ids:
            perm = db.query(Permission).filter(Permission.id == perm_id).first()
            if perm:
                rp = RolePermission(role_id=new_role.id, permission_id=perm.id)
                db.add(rp)
        db.commit()
        db.refresh(new_role)
        
    return new_role

from schemas.role import PermissionBase

@router.get("/", response_model=List[RoleOut])
def get_roles(
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("manage_roles"))
) -> Any:
    """Get all roles"""
    return db.query(Role).all()

@router.get("/permissions", response_model=List[PermissionBase])
def get_permissions(
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("manage_roles"))
) -> Any:
    """Get all permissions"""
    return db.query(Permission).all()

@router.put("/{role_id}", response_model=RoleOut)
def update_role(
    role_id: int,
    role_in: RoleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("manage_roles"))
) -> Any:
    """Update an existing role and its permissions"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Update basic info
    role.name = role_in.name
    role.description = role_in.description

    # Update permissions: Clear existing and add new
    db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
    
    if role_in.permission_ids:
        for perm_id in role_in.permission_ids:
            perm = db.query(Permission).filter(Permission.id == perm_id).first()
            if perm:
                rp = RolePermission(role_id=role.id, permission_id=perm.id)
                db.add(rp)
    
    db.commit()
    db.refresh(role)
    return role
