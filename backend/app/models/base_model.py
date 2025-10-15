"""
Base model definitions for SQLAlchemy models.
This module is separated to avoid circular imports.
"""

from datetime import datetime
from typing import Any, Type, TypeVar, Optional, Dict
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import Integer, DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from sqlalchemy.sql import func

# Type variable for model classes
ModelType = TypeVar("ModelType", bound="Base")


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Generate table name from class name
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
    """Mixin for adding a UUID field to models."""

    uuid: Mapped[str] = mapped_column(
        String(36), unique=True, index=True, default=lambda: str(uuid.uuid4())
    )


class TimeStampedMixin:
    """Mixin for adding created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )


class BaseUUIDModel(Base):
    """Base model with UUID as primary key."""

    __abstract__ = True
    id = None  # Remove the default id column
    uuid: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )


class BaseTimeStampedModel(Base):
    """Base model with timestamps."""

    __abstract__ = True
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )


class BaseUUIDTimeStampedModel(BaseUUIDModel, TimeStampedMixin):
    """Base model with UUID and timestamps."""

    __abstract__ = True


class BaseModel(PydanticBaseModel):
    """Base model for Pydantic schemas with common configurations."""

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
        }

    def dict(self, **kwargs):
        """Override dict method to handle datetime serialization."""
        data = super().model_dump(**kwargs)
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data

    @classmethod
    def from_orm(cls, obj):
        """Convert SQLAlchemy model to Pydantic model."""
        return cls.model_validate(obj)
