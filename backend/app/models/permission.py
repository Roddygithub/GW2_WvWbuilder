"""
Modèle de permission pour l'application GW2 WvW Builder.

Ce module définit le modèle Permission pour la gestion des autorisations des rôles.
"""
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base

from .association_tables import role_permissions

if TYPE_CHECKING:
    from .role import Role

class Permission(Base):
    """Modèle de permission pour les rôles utilisateurs."""
    
    __tablename__ = "permissions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    
    # Relations
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions",
        viewonly=True
    )
    
    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, name='{self.name}')>"
    
    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire pour la sérialisation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
