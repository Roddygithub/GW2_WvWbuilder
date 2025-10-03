"""
CRUD operations for Permission model.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.permission import Permission
from app.schemas.permission import PermissionCreate, PermissionUpdate
from .base import CRUDBase


class CRUDPermission(CRUDBase[Permission, PermissionCreate, PermissionUpdate]):
    """
    CRUD operations for Permission model.
    """
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[Permission]:
        """Get a permission by name."""
        return db.query(Permission).filter(Permission.name == name).first()
    
    def get_by_code(self, db: Session, *, code: str) -> Optional[Permission]:
        """Get a permission by code."""
        return db.query(Permission).filter(Permission.code == code).first()
    
    def get_multi(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        is_active: bool = None
    ) -> List[Permission]:
        """Get multiple permissions with optional filtering."""
        query = db.query(Permission)
        
        if is_active is not None:
            query = query.filter(Permission.is_active == is_active)
            
        return query.offset(skip).limit(limit).all()


# Create a singleton instance
permission = CRUDPermission(Permission)
