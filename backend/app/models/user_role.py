"""
Modèle pour la relation many-to-many entre les utilisateurs et les rôles.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .role import Role


class UserRole(Base):
    """Modèle pour la relation many-to-many entre les utilisateurs et les rôles.

    Cette classe définit la table de jointure pour les relations many-to-many
    entre les utilisateurs et les rôles.
    """

    __tablename__ = "user_roles"

    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id: Mapped[int] = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    user: Mapped["User"] = relationship("User", back_populates="role_associations")
    role: Mapped["Role"] = relationship("Role", back_populates="user_associations")

    def __repr__(self) -> str:
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"
