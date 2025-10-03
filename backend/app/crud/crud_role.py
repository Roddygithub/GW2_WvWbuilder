"""
CRUD operations for Role model.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate
from .base import CRUDBase


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    """
    CRUD operations for Role model.
    """
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[Role]:
        """Get a role by name."""
        return db.query(Role).filter(Role.name == name).first()
    
    def get_multi(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        is_active: bool = None
    ) -> List[Role]:
        """Get multiple roles with optional filtering."""
        query = db.query(Role)
        
        if is_active is not None:
            query = query.filter(Role.is_active == is_active)
            
        return query.offset(skip).limit(limit).all()


# Create a singleton instance
role = CRUDRole(Role)
