"""
Module de composition pour l'application GW2 WvW Builder.

Ce module définit le modèle Composition pour la gestion des compositions d'équipe WvW.
"""

from typing import Any, List, Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base, TimeStampedMixin

# Pour les annotations de type en cas d'imports circulaires
if TYPE_CHECKING:
    from .build import Build
    from .composition_tag import CompositionTag  # noqa: F401
    from .team import Team
    from .user import User

# Import des modèles pour éviter les imports circulaires
from .user import User
from .build import Build
from .team import Team


class Composition(Base, TimeStampedMixin):
    """Modèle de composition d'équipe WvW."""

    __tablename__ = "compositions"
    __table_args__ = {
        "extend_existing": True,  # Permet de redéfinir la table si elle existe déjà
        "sqlite_autoincrement": True,  # Active l'auto-incrémentation pour SQLite
    }

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    squad_size: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)
    game_mode: Mapped[str] = mapped_column(String(50), default="wvw", nullable=False)
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Les champs created_at et updated_at sont fournis par TimeStampedMixin

    build_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("builds.id", ondelete="SET NULL"), nullable=True, index=True
    )
    team_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Relations
    members: Mapped[List[User]] = relationship(
        "User",
        secondary="composition_members",
        back_populates="compositions",
        viewonly=True,
        lazy="selectin",
    )

    composition_tags: Mapped[List["CompositionTag"]] = relationship(
        "CompositionTag",
        back_populates="composition",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    creator: Mapped[User] = relationship(
        "User",
        back_populates="created_compositions",
        foreign_keys=[created_by],
        lazy="selectin",
    )

    build: Mapped[Optional[Build]] = relationship(
        "Build", back_populates="compositions", lazy="selectin"
    )

    team: Mapped[Optional[Team]] = relationship(
        "Team", back_populates="compositions", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Composition {self.name}>"

    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire pour la sérialisation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "squad_size": self.squad_size,
            "is_public": self.is_public,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "build_id": self.build_id,
            "team_id": self.team_id,
        }

    def __init__(self, **kwargs: Any) -> None:
        # Valider squad_size avant l'initialisation
        if "squad_size" in kwargs and kwargs["squad_size"] <= 0:
            raise ValueError("squad_size must be greater than 0")

        # Valider le statut
        valid_statuses = ["draft", "published", "archived"]
        if "status" in kwargs and kwargs["status"] not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of {valid_statuses}")

        # Valider le mode de jeu
        valid_game_modes = ["wvw", "pve", "pvp"]
        if "game_mode" in kwargs and kwargs["game_mode"] not in valid_game_modes:
            raise ValueError(f"Invalid game_mode. Must be one of {valid_game_modes}")

        super().__init__(**kwargs)

        # Assure que les valeurs par défaut sont définies si non fournies
        if not hasattr(self, "squad_size"):
            self.squad_size = 10
        if not hasattr(self, "is_public"):
            self.is_public = True
        if not hasattr(self, "status"):
            self.status = "draft"
        if not hasattr(self, "game_mode"):
            self.game_mode = "wvw"
