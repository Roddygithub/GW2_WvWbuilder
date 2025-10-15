"""
Modèle pour la relation many-to-many entre les utilisateurs et les rôles.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, func, Table
from sqlalchemy.orm import Mapped, relationship

from .base_model import Base

if TYPE_CHECKING:
    from .user import User
    from .role import Role

# Simple association table without ORM mapping
user_roles_table = Table(
    "user_roles",
    Base.metadata,
    Column(
        "user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    ),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    extend_existing=True,
)


# Use Base's registry directly without inheriting to avoid automatic columns
@Base.registry.mapped
class UserRole:
    """ORM class for user_roles with relationships (uses existing table)."""

    __table__ = user_roles_table
    __mapper_args__ = {
        "primary_key": [user_roles_table.c.user_id, user_roles_table.c.role_id]
    }

    # Relations
    user: Mapped["User"] = relationship("User", back_populates="role_associations")
    role: Mapped["Role"] = relationship("Role", back_populates="user_associations")

    def __repr__(self) -> str:
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"
