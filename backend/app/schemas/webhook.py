from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime


class WebhookBase(BaseModel):
    url: HttpUrl = Field(..., example="https://example.com/webhook")
    event_types: List[str] = Field(..., min_length=1, example=["build.create", "build.update"])
    is_active: Optional[bool] = True


class WebhookCreate(WebhookBase):
    pass


class WebhookUpdate(BaseModel):
    url: Optional[HttpUrl] = None
    event_types: Optional[List[str]] = None
    is_active: Optional[bool] = None


class WebhookInDBBase(WebhookBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Webhook(WebhookInDBBase):
    """Propriétés à retourner au client."""

    # Le secret ne doit être retourné qu'à la création.
    secret: Optional[str] = Field(None, description="Le secret du webhook, retourné uniquement lors de la création.")


class WebhookInDB(WebhookInDBBase):
    """Propriétés stockées en DB, incluant le secret."""

    secret: str


class WebhookEventBase(BaseModel):
    """Schéma de base pour les événements de webhook."""

    event_type: str = Field(..., description="Type d'événement déclencheur")
    payload: dict = Field(..., description="Données de l'événement")


class WebhookEventCreate(WebhookEventBase):
    """Schéma pour la création d'un événement de webhook."""

    pass


class WebhookEventInDB(WebhookEventBase):
    """Schéma pour un événement de webhook en base de données."""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class WebhookDeliveryBase(BaseModel):
    """Schéma de base pour les livraisons de webhooks."""

    webhook_id: int = Field(..., description="ID du webhook associé")
    event_id: int = Field(..., description="ID de l'événement associé")
    url: str = Field(..., description="URL de destination du webhook")
    status: str = Field(..., description="Statut de la livraison")
    response_status: Optional[int] = Field(None, description="Code de statut HTTP de la réponse")
    response_body: Optional[str] = Field(None, description="Corps de la réponse HTTP")
    error_message: Optional[str] = Field(None, description="Message d'erreur en cas d'échec")
    retry_count: int = Field(0, description="Nombre de tentatives de livraison")


class WebhookDeliveryCreate(WebhookDeliveryBase):
    """Schéma pour la création d'une livraison de webhook."""

    pass


class WebhookDeliveryUpdate(BaseModel):
    """Schéma pour la mise à jour d'une livraison de webhook."""

    status: Optional[str] = None
    response_status: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: Optional[int] = None
    last_attempt: Optional[datetime] = None
    next_retry: Optional[datetime] = None


class WebhookDeliveryInDB(WebhookDeliveryBase):
    """Schéma pour une livraison de webhook en base de données."""

    id: int
    created_at: datetime
    last_attempt: Optional[datetime] = None
    next_retry: Optional[datetime] = None

    class Config:
        from_attributes = True
