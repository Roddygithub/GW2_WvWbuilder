"""
Modèle de build pour l'application GW2 WvW Builder.

Ce module définit le modèle Build qui représente une configuration de personnage
avec des compétences, des armes et des attributs spécifiques pour le mode WvW de Guild Wars 2.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy import Integer, String, Boolean, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base_model import Base, TimeStampedMixin

# Tables d'association
from .association_tables import build_profession

__all__ = ["Build"]


class Build(Base, TimeStampedMixin):
    """Modèle de build pour les compositions.

    Un build représente une configuration de personnage avec des compétences, des armes et des attributs
    spécifiques pour le mode WvW de Guild Wars 2.
    """

    __tablename__ = "builds"
    __table_args__ = {"comment": "Stocke les configurations de builds pour le mode WvW de Guild Wars 2"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, comment="Identifiant unique du build")
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False, comment="Nom du build")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Description détaillée du build")
    game_mode: Mapped[str] = mapped_column(String(20), default="wvw", comment="Mode de jeu cible (wvw, pvp, pve, etc.)")
    team_size: Mapped[int] = mapped_column(Integer, default=5, comment="Taille d'équipe recommandée")
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, comment="Si le build est public ou privé")

    created_by_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID de l'utilisateur qui a créé le build",
    )
    # Les champs created_at et updated_at sont fournis par TimeStampedMixin
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), comment="Dernière mise à jour du build"
    )

    # Configuration du build (compétences, armes, etc.)
    config: Mapped[Dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict, comment="Configuration du build (compétences, armes, etc.)"
    )

    # Contraintes et exigences du build
    constraints: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, default=dict, comment="Contraintes et exigences du build"
    )

    # Relation avec l'équipe (optionnelle)
    team_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Équipe à laquelle le build est associé (optionnel)",
    )

    # Relations
    created_by: Mapped["User"] = relationship("User", back_populates="builds", lazy="selectin")
    compositions: Mapped[List["Composition"]] = relationship(
        "Composition", back_populates="build", cascade="all, delete-orphan", lazy="selectin"
    )
    # Relation many-to-many avec Profession via la table d'association build_profession
    # Cette relation est gérée à travers la table d'association build_profession
    professions: Mapped[List["Profession"]] = relationship(
        "Profession", secondary=build_profession, back_populates="builds", lazy="selectin"
    )
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="builds", lazy="selectin")
    # La relation avec EliteSpecialization est gérée via la table d'association composition_members
    # qui est liée aux compositions, pas directement aux builds

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
        }

    def has_permission(self, user_id: int, permission: str = "read") -> bool:
        """Vérifie si un utilisateur a la permission sur ce build.

        Args:
            user_id: L'ID de l'utilisateur à vérifier
            permission: La permission à vérifier ('read', 'write', 'admin')

        Returns:
            bool: True si l'utilisateur a la permission, False sinon
        """
        if self.is_owner(user_id):
            return True

        if self.is_public and permission == "read":
            return True

        if self.team and self.team.has_member(user_id):
            if permission == "read":
                return True
            if permission == "write" and self.team.is_admin(user_id):
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
