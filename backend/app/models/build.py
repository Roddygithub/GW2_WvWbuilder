<<<<<<< HEAD
from typing import List
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, JSON, DateTime, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from .build_profession import BuildProfession

# Remove circular imports by using string-based relationships
__all__ = ["Build"]

class Build(Base):
    __tablename__ = "builds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String)
    game_mode = Column(String, default="wvw")  # Could be "wvw", "pvp", etc.
    team_size = Column(Integer, default=5)  # Default to 5-man squads
    is_public = Column(Boolean, default=False)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    created_by = relationship("User", back_populates="builds")
    compositions = relationship("Composition", back_populates="build", cascade="all, delete-orphan")
    build_professions = relationship("BuildProfession", back_populates="build", cascade="all, delete-orphan")
    
    # Many-to-many relationship with Profession through BuildProfession
    professions = relationship(
        "Profession",
        secondary="build_professions",
        back_populates="builds",
        overlaps="build_professions,profession"
    )
    
    # Store build configuration as JSON for flexibility
    config = Column(JSON, nullable=False, default=dict)
    
    # Constraints and rules for the build
    constraints = Column(JSON, default=dict)  # E.g., max of 2 of same profession
    
    @property
    def owner_id(self) -> int:
        """Alias for created_by_id for API compatibility."""
        return self.created_by_id
        
    @owner_id.setter
    def owner_id(self, value: int) -> None:
        """Set the owner ID (alias for created_by_id)."""
        self.created_by_id = value

    def __repr__(self):
        return f"<Build {self.name}>"

# BuildProfession model has been moved to app.models.build_profession
=======
"""
Modèle de build pour l'application GW2 WvW Builder.

Ce module définit le modèle Build avec ses relations et méthodes associées.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING, cast

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base

# Import des tables d'association
from .association_tables import build_profession, composition_members

if TYPE_CHECKING:
    from .composition import Composition
    from .elite_specialization import EliteSpecialization
    from .profession import Profession
    from .team import Team
    from .user import User


class Build(Base):
    """Modèle de build pour les compositions.
    
    Un build représente une configuration de personnage avec des compétences, des armes et des attributs
    spécifiques pour le mode WvW de Guild Wars 2.
    """

    __tablename__ = "builds"
    __table_args__ = {
        'comment': 'Stocke les configurations de builds pour le mode WvW de Guild Wars 2'
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, comment='Identifiant unique du build')
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False, comment='Nom du build')
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment='Description détaillée du build')
    game_mode: Mapped[str] = mapped_column(String(20), default="wvw", comment='Mode de jeu cible (wvw, pvp, pve, etc.)')
    team_size: Mapped[int] = mapped_column(Integer, default=5, comment='Taille d\'équipe recommandée')
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, comment='Si le build est public ou privé')
    created_by_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment='ID de l\'utilisateur qui a créé le build'
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        comment='Date de création du build'
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        onupdate=func.now(),
        comment='Dernière mise à jour du build'
    )
    config: Mapped[Dict[str, Any]] = mapped_column(
        JSON, 
        nullable=False, 
        default=dict,
        comment='Configuration du build (compétences, armes, etc.)'
    )
    constraints: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, 
        default=dict,
        comment='Contraintes et exigences du build'
    )
    team_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("teams.id", ondelete="SET NULL"), 
        nullable=True, 
        index=True,
        comment='Équipe à laquelle le build est associé (optionnel)'
    )

    # Relations
    created_by: Mapped["User"] = relationship(
        "User", 
        back_populates="builds",
        lazy="selectin"
    )
    
    compositions: Mapped[List["Composition"]] = relationship(
        "Composition", 
        back_populates="build", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    professions: Mapped[List["Profession"]] = relationship(
        "Profession", 
        secondary=build_profession, 
        back_populates="builds",
        lazy="selectin"
    )
    
    team: Mapped[Optional["Team"]] = relationship(
        "Team", 
        back_populates="builds",
        lazy="selectin"
    )
    
    elite_specialization: Mapped[Optional["EliteSpecialization"]] = relationship(
        "EliteSpecialization",
        secondary=composition_members,
        back_populates="builds",
        viewonly=True,
        lazy="selectin"
    )

    @property
    def owner_id(self) -> int:
        """Retourne l'ID du propriétaire (alias pour created_by_id)."""
        return self.created_by_id

    @owner_id.setter
    def owner_id(self, value: int) -> None:
        """Définit l'ID du propriétaire (alias pour created_by_id)."""
        self.created_by_id = value

    @property
    def team_owner_id(self) -> Optional[int]:
        """Retourne l'ID du propriétaire de l'équipe si le build appartient à une équipe."""
        return self.team.owner_id if self.team else None

    def __repr__(self) -> str:
        return f"<Build(id={self.id}, name='{self.name}')>"

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire pour la sérialisation.
        
        Returns:
            Dict[str, Any]: Un dictionnaire contenant les données du build.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "game_mode": self.game_mode,
            "team_size": self.team_size,
            "is_public": self.is_public,
            "created_by_id": self.created_by_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "config": self.config,
            "constraints": self.constraints,
            "team_id": self.team_id,
            "profession_ids": [p.id for p in self.professions],
            "elite_specialization_id": self.elite_specialization.id if self.elite_specialization else None,
        }
    
    def has_permission(self, user_id: int, permission: str = "read") -> bool:
        """Vérifie si un utilisateur a la permission sur ce build.
        
        Args:
            user_id: L'ID de l'utilisateur à vérifier
            permission: La permission à vérifier ('read', 'write', 'admin')
            
        Returns:
            bool: True si l'utilisateur a la permission, False sinon
        """
        # Le propriétaire a toutes les permissions
        if self.created_by_id == user_id:
            return True
            
        # Les builds publics sont lisibles par tous
        if permission == "read" and self.is_public:
            return True
            
        # Vérifier les permissions de l'équipe si le build appartient à une équipe
        if self.team:
            # Vérifier si l'utilisateur est membre de l'équipe
            is_member = any(member.id == user_id for member in self.team.members)
            
            if is_member:
                if permission == "read":
                    return True
                elif permission == "write" and self.team.is_admin(user_id):
                    return True
                    
        return False
    
    def add_profession(self, profession: "Profession") -> None:
        """Ajoute une profession à ce build.
        
        Args:
            profession: La profession à ajouter
        """
        if profession not in self.professions:
            self.professions.append(profession)
    
    def remove_profession(self, profession: "Profession") -> None:
        """Supprime une profession de ce build.
        
        Args:
            profession: La profession à supprimer
        """
        if profession in self.professions:
            self.professions.remove(profession)
    
    def is_owner(self, user_id: int) -> bool:
        """Vérifie si l'utilisateur est le propriétaire du build.
        
        Args:
            user_id: L'ID de l'utilisateur à vérifier
            
        Returns:
            bool: True si l'utilisateur est le propriétaire, False sinon
        """
        return self.created_by_id == user_id
>>>>>>> a023051 (feat: optimized CRUD with Redis caching + full test coverage + docs and monitoring guide)
