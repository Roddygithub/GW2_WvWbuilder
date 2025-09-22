"""
Module de composition pour l'application GW2 WvW Builder.

Ce module définit le modèle Composition pour la gestion des compositions d'équipe WvW.
"""

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimeStampedMixin
from .association_tables import composition_members

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
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    squad_size: Mapped[int] = mapped_column(Integer, default=10)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String, default="draft", nullable=False)
    game_mode: Mapped[str] = mapped_column(String, default="wvw", nullable=False)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    build_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("builds.id"), nullable=True
    )
    team_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("teams.id"), nullable=True, index=True
    )
    
    # Relations
    members: Mapped[List[User]] = relationship(
        "User",
        secondary="composition_members",
        back_populates="compositions",
        viewonly=True,
    )
    
    composition_tags: Mapped[List["CompositionTag"]] = relationship(
        "CompositionTag", 
        back_populates="composition", 
        cascade="all, delete-orphan"
    )
    
    creator: Mapped[User] = relationship("User", foreign_keys=[created_by])
    build: Mapped[Optional[Build]] = relationship("Build", back_populates="compositions")
    team: Mapped[Optional[Team]] = relationship("Team", back_populates="compositions")
    
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
            "team_id": self.team_id
        }
