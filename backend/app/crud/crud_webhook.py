import secrets
from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.webhook import Webhook
from app.schemas.webhook import WebhookCreate, WebhookUpdate


class CRUDWebhook(CRUDBase[Webhook, WebhookCreate, WebhookUpdate]):
    async def create_with_owner(self, db: AsyncSession, *, obj_in: WebhookCreate, user_id: int) -> Webhook:
        obj_in_data = jsonable_encoder(obj_in)
        secret = secrets.token_hex(32)
        db_obj = self.model(**obj_in_data, user_id=user_id, secret=secret)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_multi_by_owner(
        self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Webhook]:
        result = await db.execute(select(self.model).where(self.model.user_id == user_id).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_multi_by_event_type(self, db: AsyncSession, *, event_type: str) -> List[Webhook]:
        """
        Récupère tous les webhooks actifs abonnés à un type d'événement spécifique.
        Utilise selectinload pour éviter les problèmes N+1 en chargeant l'utilisateur.
        """
        query = (
            select(self.model)
            .where(self.model.is_active, self.model.event_types.contains([event_type]))
            .options(selectinload(self.model.user))
        )
        result = await db.execute(query)
        return result.scalars().all()


webhook = CRUDWebhook(Webhook)
