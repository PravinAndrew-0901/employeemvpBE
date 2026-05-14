from pydantic import BaseModel
from typing import Optional, List

class PermissionBase(BaseModel):
    id: int
    name: str
    module_name: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    permission_ids: List[int] = []

class RoleOut(RoleBase):
    id: int
    is_system_role: bool
    permissions: List[PermissionBase] = []

    class Config:
        from_attributes = True
