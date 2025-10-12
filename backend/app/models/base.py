"""
Module de compatibilité pour les imports rétrocompatibles.

Ce module est maintenu pour la compatibilité avec le code existant.
Les nouvelles fonctionnalités doivent utiliser le module base_model.py.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

# Import des classes de base depuis le nouveau module
from .base_model import (
    Base,
    BaseModel,
    UUIDMixin,
    TimeStampedMixin,
    BaseUUIDModel,
    BaseTimeStampedModel,
    BaseUUIDTimeStampedModel,
)

__all__ = [
    "Base",
    "BaseModel",
    "UUIDMixin",
    "TimeStampedMixin",
    "BaseUUIDModel",
    "BaseTimeStampedModel",
    "BaseUUIDTimeStampedModel",
]


class BaseUUIDModel(Base, UUIDMixin):
    """Modèle de base avec un UUID comme identifiant unique."""

    __abstract__ = True

    id = None  # On désactive l'id auto-incrémenté
    uuid: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.uuid}>"


class BaseTimeStampedModel(Base):
    """Modèle de base avec des horodatages de création et de mise à jour."""

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)


class BaseUUIDTimeStampedModel(BaseUUIDModel, TimeStampedMixin):
    """Modèle de base avec UUID et horodatages."""

    __abstract__ = True


class BaseModel(PydanticBaseModel):
    """Base model for Pydantic schemas with common configurations."""

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}
        populate_by_name = True

    def dict(self, **kwargs) -> Dict[str, Any]:
        """Override dict method to handle datetime serialization."""
        return super().model_dump(by_alias=True, **kwargs)

    @classmethod
    def from_orm(cls, obj):
        """Convert SQLAlchemy model to Pydantic model."""
        return cls.model_validate(obj)
