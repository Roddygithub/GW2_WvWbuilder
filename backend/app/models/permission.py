"""
Modèle de permission pour l'application GW2 WvW Builder.

Ce module définit le modèle Permission pour la gestion des autorisations des rôles.
"""

from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base, TimeStampedMixin

from .association_tables import role_permissions

if TYPE_CHECKING:
    from .role import Role


class Permission(Base, TimeStampedMixin):
    """Modèle de permission pour les rôles utilisateurs."""

    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Les champs created_at et updated_at sont fournis par TimeStampedMixin

    # Relations
    roles: Mapped[List["Role"]] = relationship(
        "Role", secondary=role_permissions, back_populates="permissions", viewonly=True
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
