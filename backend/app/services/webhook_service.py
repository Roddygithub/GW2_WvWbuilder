"""
Webhook Service

This module provides functionality for managing and sending webhooks asynchronously.
"""

import asyncio
import hmac
import hashlib
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar

import httpx
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_async_db
from app.models.webhook import Webhook
from app.schemas.webhook import WebhookCreate, WebhookUpdate

# Configure logging
logger = logging.getLogger(__name__)

# Webhook configuration
MAX_RETRIES = 3
INITIAL_BACKOFF_DELAY = 1.0  # seconds
MAX_BACKOFF_DELAY = 30.0  # seconds
TIMEOUT = 10.0  # seconds

# Headers to include in webhook requests
DEFAULT_HEADERS = {"User-Agent": f"GW2WvWBuilder-Webhooks/{settings.VERSION}", "Content-Type": "application/json"}

# Type variables for generic typing
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class WebhookService:
    """Service for managing webhooks and their deliveries."""

    def __init__(self, db: AsyncSession):
        """Initialize the WebhookService with a database session."""
        self.db = db
        self.model = Webhook

    async def create_webhook(self, webhook_in: WebhookCreate, user_id: int) -> Webhook:
        """Create a new webhook.

        Args:
            webhook_in: Webhook data
            user_id: ID of the user creating the webhook

        Returns:
            Webhook: The created webhook

        Raises:
            HTTPException: If there's an error creating the webhook
        """
        try:
            # Generate a secure secret key
            secret = os.urandom(32).hex()

            # Create the webhook in the database
            db_webhook = Webhook(
                **webhook_in.dict(),
                user_id=user_id,
                secret=secret,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            self.db.add(db_webhook)
            await self.db.commit()
            await self.db.refresh(db_webhook)

            logger.info(f"Created webhook {db_webhook.id} for user {user_id}")
            return db_webhook

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create webhook: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create webhook: {str(e)}"
            )

    async def get_webhook(self, webhook_id: int, user_id: Optional[int] = None) -> Optional[Webhook]:
        """Get a webhook by ID, optionally checking ownership.

        Args:
            webhook_id: ID of the webhook to retrieve
            user_id: Optional ID of the user who owns the webhook

        Returns:
            Optional[Webhook]: The webhook if found and owned by the user (if user_id provided), None otherwise
        """
        try:
            query = select(Webhook).where(Webhook.id == webhook_id)

            # If user_id is provided, ensure the webhook belongs to that user
            if user_id is not None:
                query = query.where(Webhook.user_id == user_id)

            result = await self.db.execute(query)
            return result.scalars().first()

        except Exception as e:
            logger.error(f"Error fetching webhook {webhook_id}: {str(e)}", exc_info=True)
            return None

    async def get_webhooks(
        self, user_id: Optional[int] = None, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None
    ) -> List[Webhook]:
        """Get a paginated list of webhooks, optionally filtered by user and other criteria.

        Args:
            user_id: Optional ID of the user to filter by
            skip: Number of items to skip
            limit: Maximum number of items to return
            filters: Additional filter criteria

        Returns:
            List[Webhook]: List of webhooks matching the criteria
        """
        try:
            query = select(Webhook)

            # Apply user filter if user_id is provided
            if user_id is not None:
                query = query.where(Webhook.user_id == user_id)

            # Apply additional filters if provided
            if filters:
                for field, value in filters.items():
                    if hasattr(Webhook, field):
                        query = query.where(getattr(Webhook, field) == value)

            # Apply pagination and ordering
            query = query.order_by(Webhook.created_at.desc()).offset(skip).limit(limit)

            result = await self.db.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error fetching webhooks: {str(e)}", exc_info=True)
            return []
        return db.query(Webhook).filter(Webhook.user_id == user_id).offset(skip).limit(limit).all()

    @staticmethod
    def update_webhook(db: Session, webhook_id: int, user_id: int, webhook_in: WebhookUpdate) -> Optional[Webhook]:
        """Met à jour un webhook existant."""
        db_webhook = WebhookService.get_webhook(db, webhook_id, user_id)
        if not db_webhook:
            return None

        update_data = webhook_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_webhook, field, value)

        db_webhook.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_webhook)
        return db_webhook

    @staticmethod
    def delete_webhook(db: Session, webhook_id: int, user_id: int) -> bool:
        """Supprime un webhook."""
        db_webhook = WebhookService.get_webhook(db, webhook_id, user_id)
        if not db_webhook:
            return False

        db.delete(db_webhook)
        db.commit()
        return True

    @staticmethod
    def generate_signature(secret: str, payload: bytes) -> str:
        """Génère une signature HMAC pour le payload."""
        return hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256).hexdigest()

    @staticmethod
    async def dispatch_webhook(
        db: Session, event_type: str, payload: Dict[str, Any], user_id: Optional[int] = None
    ) -> None:
        """
        Envoie un événement à tous les webhooks abonnés à cet événement.

        Args:
            db: Session de base de données
            event_type: Type d'événement (ex: 'build.create', 'build.update')
            payload: Données à envoyer dans le webhook
            user_id: ID de l'utilisateur concerné (optionnel)
        """
        query = db.query(Webhook).filter(Webhook.is_active, Webhook.event_types.any(event_type))

        if user_id:
            query = query.filter(Webhook.user_id == user_id)

        webhooks = query.all()

        if not webhooks:
            return

        # Sérialiser le payload une seule fois
        try:
            payload_json = json.dumps(payload, default=str).encode()
        except TypeError as e:
            logger.error(f"Failed to serialize webhook payload for event {event_type}: {e}", exc_info=True)
            return

        async with httpx.AsyncClient(timeout=settings.WEBHOOK_TIMEOUT) as client:
            tasks = [
                WebhookService._send_single_webhook(client, webhook, event_type, payload_json) for webhook in webhooks
            ]
            await asyncio.gather(*tasks, return_exceptions=False)  # exceptions are handled in _send_single_webhook

    @staticmethod
    async def _send_single_webhook(
        client: httpx.AsyncClient, webhook: Webhook, event_type: str, payload_json: bytes
    ) -> None:
        """Envoie un événement à un seul webhook avec une logique de tentatives."""
        signature = WebhookService.generate_signature(webhook.secret, payload_json)
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Event": event_type,
            "X-Webhook-Signature": f"sha256={signature}",
            "User-Agent": f"GW2_WvWbuilder/{settings.VERSION}",
        }

        delay = INITIAL_BACKOFF_DELAY
        for attempt in range(MAX_RETRIES):
            try:
                response = await client.post(str(webhook.url), content=payload_json, headers=headers)
                response.raise_for_status()  # Lève une exception pour les statuts 4xx/5xx
                logger.info(
                    f"Webhook {webhook.id} sent to {webhook.url} on attempt {attempt + 1} - Status: {response.status_code}"
                )
                return  # Succès, on sort de la fonction
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                logger.warning(
                    f"Attempt {attempt + 1}/{MAX_RETRIES} failed for webhook {webhook.id} to {webhook.url}: {e}"
                )
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    logger.error(
                        f"Failed to send webhook {webhook.id} to {webhook.url} after {MAX_RETRIES} attempts. Disabling it.",
                        exc_info=False,
                    )
                    # This part runs synchronously within the async function.
                    # It's safe as long as it's quick and not awaited.
                    webhook.is_active = False
                    # The session that dispatched this event will commit this change.
                    logger.info(f"Webhook {webhook.id} has been disabled due to repeated failures.")


async def get_webhook_service(db: AsyncSession = Depends(get_async_db)) -> WebhookService:
    """Dependency that provides a WebhookService instance with a database session.

    Args:
        db: Async database session

    Returns:
        WebhookService: An instance of WebhookService
    """
    return WebhookService(db=db)
