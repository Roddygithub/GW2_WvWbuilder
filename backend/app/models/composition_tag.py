"""
Module d'étiquette de composition pour l'application GW2 WvW Builder.

Ce module définit le modèle CompositionTag pour gérer la relation many-to-many
entre les compositions et les balises.
"""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimeStampedMixin

# Pour les annotations de type en cas d'imports circulaires
if TYPE_CHECKING:
    from .composition import Composition  # noqa: F401


class CompositionTag(Base, TimeStampedMixin):
    """
    Modèle d'étiquette de composition.

    Ce modèle établit une relation many-to-many entre les compositions et les balises.
    """

    __tablename__ = "composition_tags"
    __table_args__ = {"extend_existing": True}  # Permet de redéfinir la table si elle existe déjà

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    composition_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("compositions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relations
    composition: Mapped["Composition"] = relationship("Composition", back_populates="composition_tags")
    tag: Mapped["Tag"] = relationship("Tag", back_populates="composition_tags")

    def __repr__(self) -> str:
        return f"<CompositionTag(composition_id={self.composition_id}, tag_id={self.tag_id})>"

    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire pour la sérialisation."""
        return {
            "id": self.id,
            "composition_id": self.composition_id,
            "tag_id": self.tag_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
