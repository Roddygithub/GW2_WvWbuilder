"""
Modèle de rôle pour l'application GW2 WvW Builder.

Ce module définit le modèle Role avec ses relations et méthodes associées.
"""
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base

from .association_tables import user_roles, role_permissions

if TYPE_CHECKING:
    from .permission import Permission
    from .user import User


class Role(Base):
    """Modèle de rôle pour les autorisations des utilisateurs."""

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    permission_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # Relations
    users: Mapped[List["User"]] = relationship(
        "User", secondary=user_roles, back_populates="roles", viewonly=True
    )
    
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission", secondary=role_permissions, back_populates="roles", viewonly=True
    )

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}')>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Role):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash((self.id, self.name))
