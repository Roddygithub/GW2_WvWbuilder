"""
Modèle d'équipe pour l'application GW2 WvW Builder.

Ce module définit le modèle Team avec ses relations et méthodes associées.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base
from .enums import TeamRole, TeamStatus

if TYPE_CHECKING:
    from .build import Build
    from .composition import Composition
    from .team_member import TeamMember
    from .user import User



class Team(Base):
    """Modèle d'équipe pour GW2 WvW Builder."""

    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    status: Mapped[TeamStatus] = mapped_column(
        Enum(TeamStatus), default=TeamStatus.ACTIVE, nullable=False
    )
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Relations
    owner: Mapped["User"] = relationship(
        "User", 
        back_populates="owned_teams",
        foreign_keys=[owner_id]
    )
    
    # Relation avec les membres via la table d'association TeamMember
    members: Mapped[List["User"]] = relationship(
        "User",
        secondary="team_members",
        primaryjoin="and_(Team.id == TeamMember.team_id, TeamMember.is_active == True)",
        secondaryjoin="User.id == TeamMember.user_id",
        viewonly=True,
        overlaps="member_associations"
    )
    
    # Relation avec les associations de membres (pour accéder aux détails de la relation)
    member_associations: Mapped[List["TeamMember"]] = relationship(
        "TeamMember",
        back_populates="team",
        cascade="all, delete-orphan",
        overlaps="members"
    )
    
    builds: Mapped[List["Build"]] = relationship(
        "Build", 
        back_populates="team",
        cascade="all, delete-orphan"
    )
    
    compositions: Mapped[List["Composition"]] = relationship(
        "Composition", 
        back_populates="team",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Team(id={self.id}, name='{self.name}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire pour la sérialisation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "is_public": self.is_public,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def add_member(self, user: "User", role: TeamRole = TeamRole.MEMBER, is_admin: bool = False) -> None:
        """
        Ajoute un membre à l'équipe avec le rôle et les permissions spécifiés.
        
        Args:
            user: L'utilisateur à ajouter à l'équipe
            role: Le rôle de l'utilisateur dans l'équipe
            is_admin: Si l'utilisateur est administrateur de l'équipe
        """
        if user not in self.members:
            from .team_member import TeamMember
            
            # Créer une nouvelle association TeamMember
            team_member = TeamMember(
                team_id=self.id,
                user_id=user.id,
                role=role,
                is_admin=is_admin,
                is_active=True
            )
            
            # Ajouter l'association à la session
            from app.db.session import SessionLocal
            db = SessionLocal()
            try:
                db.add(team_member)
                db.commit()
                # Rafraîchir les relations
                db.refresh(team_member)
            except Exception as e:
                db.rollback()
                raise e
            finally:
                db.close()

    def remove_member(self, user: "User") -> None:
        """Supprime un membre de l'équipe."""
        if user in self.members:
            self.members.remove(user)
            # Note: Cette opération nécessite une session de base de données
            from sqlalchemy import delete
            from app.db.session import SessionLocal
            
            db = SessionLocal()
            try:
                stmt = delete(team_members).where(
                    (team_members.c.team_id == self.id) & 
                    (team_members.c.user_id == user.id)
                )
                db.execute(stmt)
                db.commit()
            except Exception as e:
                db.rollback()
                raise e
            finally:
                db.close()

    def change_member_role(self, user: "User", new_role: TeamRole) -> None:
        """Modifie le rôle d'un membre dans l'équipe."""
        if user in self.members:
            # Mise à jour du rôle dans la table d'association
            # Note: Cette opération nécessite une session de base de données
            from sqlalchemy import update
            from app.db.session import SessionLocal
            
            db = SessionLocal()
            try:
                stmt = (
                    update(team_members)
                    .where(
                        (team_members.c.team_id == self.id) & 
                        (team_members.c.user_id == user.id)
                    )
                    .values(role=new_role, updated_at=func.now())
                )
                db.execute(stmt)
                db.commit()
            except Exception as e:
                db.rollback()
                raise e
            finally:
                db.close()
