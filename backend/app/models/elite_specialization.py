"""
Modèle de spécialisation d'élite pour l'application GW2 WvW Builder.

Ce module définit le modèle EliteSpecialization qui représente les spécialisations d'élite
disponibles pour chaque profession dans Guild Wars 2, comme le Berserker pour le Guerrier
ou le Dragonhunter pour le Gardien.
"""

from datetime import datetime
from typing import Any, Dict, Optional, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base_model import Base, TimeStampedMixin

if TYPE_CHECKING:
    from .profession import Profession


class EliteSpecialization(Base, TimeStampedMixin):
    """Modèle de spécialisation d'élite pour les professions.

    Une spécialisation d'élite est une variante avancée d'une profession qui modifie
    significativement son style de jeu en ajoutant de nouvelles compétences, armes
    et mécaniques uniques.
    """

    __tablename__ = "elite_specializations"
    __table_args__ = ({"comment": "Spécialisations d'élite disponibles pour chaque profession dans GW2"},)

    # Identifiant unique de la spécialisation d'élite
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, comment="Identifiant unique de la spécialisation d'élite"
    )

    # Nom de la spécialisation d'élite (ex: "Berserker", "Dragonhunter")
    name: Mapped[str] = mapped_column(
        String(50), index=True, nullable=False, comment="Nom de la spécialisation d'élite"
    )

    # Clé étrangère vers la profession parente
    # Clé étrangère vers la profession parente
    profession_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("professions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la profession parente",
    )

    # URL de l'icône de la spécialisation
    icon_url: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="URL de l'icône représentant la spécialisation"
    )

    # Description détaillée de la spécialisation
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Description détaillée de la spécialisation et de ses mécaniques"
    )

    # Type d'arme ajouté par cette spécialisation
    weapon_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="Type d'arme ajouté par cette spécialisation"
    )

    # URL de l'image de fond de la spécialisation
    background_url: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="URL de l'image de fond de la spécialisation"
    )

    # Indique si la spécialisation est active dans le jeu
    is_active: Mapped[bool] = mapped_column(
        default=True, nullable=False, comment="Indique si la spécialisation est actuellement disponible dans le jeu"
    )

    # Horodatages de création et de mise à jour
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="Date et heure de création de l'enregistrement"
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), comment="Date et heure de la dernière mise à jour"
    )

    # Relations
    profession: Mapped["Profession"] = relationship(
        "Profession", back_populates="elite_specializations", lazy="selectin"
    )

    # La relation avec les builds est gérée via la table d'association composition_members
    # qui est liée aux compositions, pas directement aux builds
    # Cette relation est commentée car elle nécessite une refonte du modèle de données
    # pour être cohérente avec la structure actuelle
    # builds: Mapped[List["Build"]] = relationship(
    #     "Build",
    #     secondary="composition_members",
    #     viewonly=True,
    #     lazy="selectin"
    # )

    def __repr__(self) -> str:
        return f"<EliteSpecialization(id={self.id}, name='{self.name}')>"

    def to_dict(self, include_related: bool = False) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire pour la sérialisation."""
        result = {
            "id": self.id,
            "name": self.name,
            "profession_id": self.profession_id,
            "icon_url": self.icon_url,
            "background_url": self.background_url,
            "weapon_type": self.weapon_type,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_related:
            result["profession"] = self.profession.to_dict() if self.profession else None
            result["builds"] = [build.to_dict() for build in self.builds]

        return result

    def is_compatible_with_profession(self, profession_id: int) -> bool:
        """Vérifie si cette spécialisation est compatible avec une profession donnée."""
        return self.profession_id == profession_id

    # Méthode commentée car elle nécessite une refonte du modèle de données
    # def get_related_builds(self, limit: int = 10) -> List["Build"]:
    #     """Récupère une liste de builds populaires utilisant cette spécialisation."""
    #     # Implémentation simplifiée
    #     return sorted(self.builds, key=lambda b: len(b.composition_members), reverse=True)[:limit]
