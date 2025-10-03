"""
Modèle utilisateur pour l'application GW2 WvW Builder.

Ce module définit le modèle User avec ses relations et méthodes associées.
"""
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base

# Import des tables de jonction
from .association_tables import composition_members, user_roles

if TYPE_CHECKING:
    from .build import Build
    from .composition import Composition
    from .role import Role
    from .team import Team
    from .team_member import TeamMember
    from .token_models import Token


class User(Base):
    """Modèle utilisateur avec authentification et autorisations."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Relations
    compositions: Mapped[List["Composition"]] = relationship(
        "Composition",
        secondary=composition_members,
        back_populates="members",
        viewonly=True,
    )

    roles: Mapped[List["Role"]] = relationship(
        "Role", secondary=user_roles, back_populates="users", viewonly=True
    )

    builds: Mapped[List["Build"]] = relationship("Build", back_populates="created_by")
    tokens: Mapped[List["Token"]] = relationship(
        "Token", back_populates="user", cascade="all, delete-orphan"
    )
    
    # Relations avec les équipes
    owned_teams: Mapped[List["Team"]] = relationship(
        "Team", 
        back_populates="owner",
        foreign_keys="Team.owner_id",
        cascade="all, delete-orphan"
    )
    
    # Relation avec les équipes via la table d'association TeamMember
    teams: Mapped[List["Team"]] = relationship(
        "Team",
        secondary="team_members",
        primaryjoin="and_(User.id == TeamMember.user_id, TeamMember.is_active == True)",
        secondaryjoin="Team.id == TeamMember.team_id",
        viewonly=True,
        overlaps="team_associations"
    )
    
    # Relation avec les associations d'équipe (pour accéder aux détails de la relation)
    team_associations: Mapped[List["TeamMember"]] = relationship(
        "TeamMember",
        back_populates="user",
        cascade="all, delete-orphan",
        overlaps="teams"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash((self.id, self.username, self.email))
