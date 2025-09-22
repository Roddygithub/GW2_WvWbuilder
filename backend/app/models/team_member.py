"""
Modèle pour les membres d'équipe dans l'application GW2 WvW Builder.

Ce module définit le modèle TeamMember qui représente la relation many-to-many
entre les utilisateurs et les équipes, avec des attributs supplémentaires.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import TeamRole

if TYPE_CHECKING:
    from .user import User
    from .team import Team

# La table d'association est définie dans association_tables.py


class TeamMember(Base):
    """
    Modèle représentant un membre d'une équipe avec son rôle et ses permissions.
    
    Cette classe est utilisée comme modèle pour les requêtes qui nécessitent
    d'accéder aux attributs de la relation entre un utilisateur et une équipe.
    """
    __tablename__ = "team_members"
    
    # Clés primaires composées
    team_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("teams.id", ondelete="CASCADE"), 
        primary_key=True,
        index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        primary_key=True,
        index=True
    )
    
    # Attributs de la relation
    role: Mapped[TeamRole] = mapped_column(
        default=TeamRole.MEMBER,
        nullable=False,
        index=True
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        nullable=False,
        index=True
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    left_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True, 
        nullable=False,
        index=True
    )
    
    # Relations
    user: Mapped["User"] = relationship("User", back_populates="team_associations")
    team: Mapped["Team"] = relationship("Team", back_populates="member_associations")
    
    def __repr__(self) -> str:
        return f"<TeamMember(team_id={self.team_id}, user_id={self.user_id}, role={self.role}, is_admin={self.is_admin})>"
    
    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire pour la sérialisation."""
        return {
            "team_id": self.team_id,
            "user_id": self.user_id,
            "role": self.role.value,
            "is_admin": self.is_admin,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "left_at": self.left_at.isoformat() if self.left_at else None,
            "is_active": self.is_active,
        }
