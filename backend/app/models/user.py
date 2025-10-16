"""
Modèle utilisateur pour l'application GW2 WvW Builder.

Ce module définit le modèle User avec ses relations et méthodes associées.
"""

from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base, TimeStampedMixin

# Import des tables de jonction
from .association_tables import composition_members
from .user_role import UserRole, user_roles_table

if TYPE_CHECKING:
    from .build import Build
    from .composition import Composition
    from .role import Role
    from .team import Team
    from .team_member import TeamMember
    from .token_models import Token


class User(Base, TimeStampedMixin):
    """Modèle utilisateur avec authentification et autorisations."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(
        String, unique=True, index=True, nullable=True
    )
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    # Les champs created_at et updated_at sont fournis par TimeStampedMixin

    # Relations
    # Compositions où l'utilisateur est membre
    compositions: Mapped[List["Composition"]] = relationship(
        "Composition",
        secondary=composition_members,
        back_populates="members",
        viewonly=True,
    )

    # Compositions créées par l'utilisateur
    created_compositions: Mapped[List["Composition"]] = relationship(
        "Composition",
        back_populates="creator",
        foreign_keys="Composition.created_by",
        viewonly=True,
    )

    # Relations many-to-many avec les rôles via le modèle UserRole
    role_associations: Mapped[List["UserRole"]] = relationship(back_populates="user")
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary=user_roles_table,
        back_populates="users",
        lazy="selectin",
        viewonly=True,
        overlaps="role_associations",
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
        cascade="all, delete-orphan",
    )

    # Relation avec les équipes via la table d'association TeamMember
    teams: Mapped[List["Team"]] = relationship(
        "Team",
        secondary="team_members",
        primaryjoin="and_(User.id == TeamMember.user_id, TeamMember.is_active == True)",
        secondaryjoin="Team.id == TeamMember.team_id",
        viewonly=True,
        overlaps="team_associations",
    )

    # Relation avec les associations d'équipe (pour accéder aux détails de la relation)
    team_associations: Mapped[List["TeamMember"]] = relationship(
        "TeamMember",
        back_populates="user",
        cascade="all, delete-orphan",
        overlaps="teams",
    )

    # Relation avec les webhooks
    webhooks: Mapped[List["Webhook"]] = relationship(
        "Webhook", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

    def get_auth_token(self) -> str:
        """
        Génère un jeton d'authentification pour l'utilisateur.

        Returns:
            str: Un jeton JWT pour l'authentification
        """
        from app.core.security.jwt import create_access_token

        return create_access_token(subject=str(self.id))

    # Compatibility for tests that expect dict-like access
    def __getitem__(self, key: str) -> str:
        if key == "access_token":
            return self.get_auth_token()
        raise KeyError(key)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash((self.id, self.username, self.email))
