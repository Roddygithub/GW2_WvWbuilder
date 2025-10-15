"""
Modèle de profession pour l'application GW2 WvW Builder.

Ce module définit le modèle Profession qui représente les différentes classes de personnage
jouables dans Guild Wars 2, ainsi que leurs relations avec les spécialisations d'élite et les builds.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base_model import Base, TimeStampedMixin

# Import des tables d'association
from .association_tables import build_profession

if TYPE_CHECKING:
    from .build import Build
    from .elite_specialization import EliteSpecialization


class Profession(Base, TimeStampedMixin):
    """Modèle de profession (classe) dans Guild Wars 2.

    Une profession représente une classe de personnage jouable dans Guild Wars 2,
    comme Guerrier, Gardien, Voleur, etc. Chaque profession peut avoir plusieurs
    spécialisations d'élite qui modifient son style de jeu.
    """

    __tablename__ = "professions"
    __table_args__ = {
        "comment": "Stocke les différentes professions (classes) de Guild Wars 2"
    }

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        comment="Identifiant unique de la profession",
    )

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
        comment="Nom de la profession (ex: Guerrier, Gardien, Voleur)",
    )

    icon_url: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="URL de l'icône représentant la profession"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Description de la profession et de son style de jeu",
    )

    game_modes: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        nullable=True,
        default=[],
        comment="Liste des modes de jeu où cette profession est viable (wvw, pvp, pve)",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="Indique si la profession est actuellement disponible dans le jeu",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Date de création de l'entrée",
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        comment="Date de dernière mise à jour de l'entrée",
    )

    # Relations
    elite_specializations: Mapped[List["EliteSpecialization"]] = relationship(
        "EliteSpecialization",
        back_populates="profession",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="EliteSpecialization.name",
    )

    builds: Mapped[List["Build"]] = relationship(
        "Build",
        secondary=build_profession,
        back_populates="professions",
        viewonly=True,
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Profession(id={self.id}, name='{self.name}')>"

    def to_dict(self, include_related: bool = False) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire pour la sérialisation.

        Args:
            include_related: Si True, inclut les objets liés (spécialisations d'élite)

        Returns:
            Dict[str, Any]: Un dictionnaire contenant les données de la profession
        """
        result = {
            "id": self.id,
            "name": self.name,
            "icon_url": self.icon_url,
            "description": self.description,
            "game_modes": self.game_modes or [],
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_related:
            result["elite_specializations"] = [
                es.to_dict() for es in self.elite_specializations
            ]
        else:
            result["elite_specialization_ids"] = [
                es.id for es in self.elite_specializations
            ]

        return result

    def is_viable_for_mode(self, game_mode: str) -> bool:
        """Vérifie si la profession est viable pour un mode de jeu donné.

        Args:
            game_mode: Le mode de jeu à vérifier (wvw, pvp, pve)

        Returns:
            bool: True si la profession est viable pour ce mode, False sinon
        """
        if not self.game_modes:
            return False
        return game_mode.lower() in [mode.lower() for mode in self.game_modes]

    def add_elite_specialization(self, elite_spec: "EliteSpecialization") -> None:
        """Ajoute une spécialisation d'élite à cette profession.

        Args:
            elite_spec: La spécialisation d'élite à ajouter

        Raises:
            ValueError: Si la spécialisation appartient déjà à une autre profession
        """
        if elite_spec.profession_id is not None and elite_spec.profession_id != self.id:
            raise ValueError(
                "Cette spécialisation appartient déjà à une autre profession"
            )

        if elite_spec not in self.elite_specializations:
            self.elite_specializations.append(elite_spec)
            elite_spec.profession = self

    def remove_elite_specialization(self, elite_spec: "EliteSpecialization") -> None:
        """Supprime une spécialisation d'élite de cette profession.

        Args:
            elite_spec: La spécialisation d'élite à supprimer
        """
        if elite_spec in self.elite_specializations:
            self.elite_specializations.remove(elite_spec)
            elite_spec.profession = None

    def get_elite_specialization_by_name(
        self, name: str
    ) -> Optional["EliteSpecialization"]:
        """Récupère une spécialisation d'élite par son nom.

        Args:
            name: Le nom de la spécialisation d'élite à récupérer

        Returns:
            Optional[EliteSpecialization]: La spécialisation d'élite si trouvée, None sinon
        """
        return next(
            (
                es
                for es in self.elite_specializations
                if es.name.lower() == name.lower()
            ),
            None,
        )
