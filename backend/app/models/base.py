"""
Module de base pour les modèles SQLAlchemy.

Ce module fournit les classes de base pour tous les modèles de l'application.
"""

import uuid
from datetime import datetime
from typing import Any, TypeVar, Type, Optional, Dict
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import Integer, DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from sqlalchemy.sql import func

# Type variable for model classes
ModelType = TypeVar("ModelType", bound="Base")


class Base(DeclarativeBase):
    """Classe de base pour tous les modèles SQLAlchemy."""

    # Ajout d'un ID de type générique pour faciliter le typage
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Génère automatiquement le nom de la table à partir du nom de la classe
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.id}>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model instance to a dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @classmethod
    def from_dict(cls: Type[ModelType], data: Dict[str, Any]) -> ModelType:
        """Create a model instance from a dictionary."""
        return cls(**data)


class UUIDMixin:
    """Mixin pour ajouter un champ UUID aux modèles."""

    uuid: Mapped[str] = mapped_column(
        String(36), unique=True, index=True, default=lambda: str(uuid.uuid4())
    )


class TimeStampedMixin:
    """Mixin pour ajouter des champs de date de création et de mise à jour."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )


class BaseUUIDModel(Base, UUIDMixin):
    """Modèle de base avec un UUID comme identifiant unique."""

    __abstract__ = True

    id = None  # On désactive l'id auto-incrémenté
    uuid: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.uuid}>"


class BaseTimeStampedModel(Base):
    """Modèle de base avec des horodatages de création et de mise à jour."""

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )


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
