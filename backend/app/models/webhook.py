from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

from sqlalchemy import (
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    JSON,
    Text,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class WebhookEventType(str, Enum):
    """Types d'événements pris en charge par les webhooks."""

    BUILD_CREATED = "build.created"
    BUILD_UPDATED = "build.updated"
    BUILD_DELETED = "build.deleted"
    USER_SIGNUP = "user.signup"
    TEAM_INVITE = "team.invite"
    TEAM_JOIN = "team.join"
    TEAM_LEAVE = "team.leave"
    COMPOSITION_CREATED = "composition.created"
    COMPOSITION_UPDATED = "composition.updated"
    COMPOSITION_DELETED = "composition.deleted"


class WebhookDeliveryStatus(str, Enum):
    """Statuts possibles d'une livraison de webhook."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"


class Webhook(Base):
    """Modèle pour les webhooks."""

    __tablename__ = "webhooks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    secret: Mapped[str] = mapped_column(String, nullable=False)
    event_types: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="webhooks")

    def __repr__(self) -> str:
        return f"<Webhook(id={self.id}, url='{self.url}', user_id={self.user_id})>"


class WebhookEvent(Base):
    """Modèle pour les événements de webhook."""

    __tablename__ = "webhook_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_type: Mapped[WebhookEventType] = mapped_column(
        SQLEnum(WebhookEventType), nullable=False, index=True
    )
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    # Relations
    deliveries: Mapped[List["WebhookDelivery"]] = relationship(
        "WebhookDelivery", back_populates="event", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<WebhookEvent(id={self.id}, event_type='{self.event_type}')>"


class WebhookDelivery(Base):
    """Modèle pour le suivi des livraisons de webhooks."""

    __tablename__ = "webhook_deliveries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[WebhookDeliveryStatus] = mapped_column(
        SQLEnum(WebhookDeliveryStatus),
        default=WebhookDeliveryStatus.PENDING,
        nullable=False,
        index=True,
    )
    response_status: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    last_attempt: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_retry: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Clés étrangères
    webhook_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("webhooks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("webhook_events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relations
    webhook: Mapped[Webhook] = relationship("Webhook", back_populates="deliveries")
    event: Mapped[WebhookEvent] = relationship(
        "WebhookEvent", back_populates="deliveries"
    )

    def __repr__(self) -> str:
        return f"<WebhookDelivery(id={self.id}, status='{self.status}', webhook_id={self.webhook_id}')>"


# Mise à jour de la relation dans le modèle Webhook
Webhook.deliveries = relationship(
    "WebhookDelivery", back_populates="webhook", cascade="all, delete-orphan"
)
