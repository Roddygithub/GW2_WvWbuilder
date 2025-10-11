"""
Modèle de balise pour l'application GW2 WvW Builder.

Ce module définit le modèle Tag pour la gestion des balises génériques.
"""

from typing import List, Optional, Dict, Any, TYPE_CHECKING

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimeStampedMixin

# Pour les annotations de type en cas d'imports circulaires
if TYPE_CHECKING:
    from .composition_tag import CompositionTag  # noqa: F401


class Tag(Base, TimeStampedMixin):
    """
    Modèle de balise pour le marquage des compositions.
    """

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)

    # Relations
    composition_tags: Mapped[List["CompositionTag"]] = relationship(
        "CompositionTag", back_populates="tag", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name='{self.name}')>"

    def to_dict(self, include_compositions: bool = False) -> Dict[str, Any]:
        """
        Convertit l'objet en dictionnaire pour la sérialisation.

        Args:
            include_compositions: Si True, inclut les compositions associées

        Returns:
            Un dictionnaire représentant la balise
        """
        result = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_compositions and self.composition_tags:
            result["compositions"] = [
                {
                    "id": ct.composition.id,
                    "name": ct.composition.name,
                    "added_at": ct.created_at.isoformat() if ct.created_at else None,
                }
                for ct in self.composition_tags
            ]

        return result
