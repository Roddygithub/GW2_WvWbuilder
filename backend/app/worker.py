import httpx
import logging
from typing import Dict, Any

from arq import create_pool
from arq.connections import RedisSettings

from app.core.config import settings
from app.core.webhook_helpers import generate_webhook_signature
from app.db.session import SessionLocal

# L'importation de crud_webhook est déplacée dans la fonction send_webhook pour éviter les importations circulaires

logger = logging.getLogger(__name__)

MAX_RETRIES = 5


async def send_webhook(
    ctx: Dict[str, Any], webhook_id: int, event_type: str, payload: Dict[str, Any]
) -> None:
    """
    Envoie un payload de webhook à une URL de destination.

    Cette fonction est une tâche `arq` qui gère l'envoi d'un webhook, y compris
    la signature de la requête, la gestion des erreurs HTTP et les tentatives multiples
    avec un délai exponentiel. Si un webhook échoue de manière répétée, il est
    automatiquement désactivé.
    """
    from app.crud import (
        webhook as crud_webhook,
    )  # Import différé pour éviter les importations circulaires

    db = SessionLocal()
    try:
        webhook = await crud_webhook.get(db, id=webhook_id)
        if not webhook or not webhook.is_active:
            logger.info(
                f"Webhook {webhook_id} non trouvé ou inactif. Annulation de l'envoi."
            )
            return

        signature = generate_webhook_signature(webhook.secret, payload)
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook.url, json=payload, headers=headers, timeout=10
            )
            response.raise_for_status()  # Lève une exception pour les statuts 4xx/5xx

        logger.info(
            f"Webhook {webhook_id} pour l'événement {event_type} envoyé avec succès à {webhook.url}"
        )

    except httpx.HTTPStatusError as e:
        logger.error(
            f"Échec de l'envoi du webhook {webhook_id} à {webhook.url}. Statut: {e.response.status_code}. Tentative {ctx.get('job_try', 1)}/{MAX_RETRIES}"
        )
        if ctx.get("job_try", 1) >= MAX_RETRIES:
            logger.warning(
                f"Le webhook {webhook_id} a échoué après {MAX_RETRIES} tentatives. Désactivation."
            )
            await crud_webhook.update(db, db_obj=webhook, obj_in={"is_active": False})
        raise e  # Arq va retenter la tâche
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'envoi du webhook {webhook_id}: {e}")
        raise e
    finally:
        await db.close()


async def dispatch_webhook_event(event_type: str, payload: Dict[str, Any]) -> None:
    """
    Récupère les webhooks abonnés à un événement et met en file d'attente les tâches d'envoi.

    Args:
        event_type: Le type d'événement qui s'est produit (ex: "build.create").
        payload: Les données associées à l'événement.
    """
    db = SessionLocal()
    try:
        webhooks = await crud_webhook.get_multi_by_event_type(db, event_type=event_type)
        for webhook in webhooks:
            await arq_pool.enqueue_job("send_webhook", webhook.id, event_type, payload)
    finally:
        await db.close()


def get_redis_settings() -> RedisSettings:
    """Retourne les paramètres Redis en fonction de l'environnement."""
    if settings.TESTING:
        # Utilise une base de données Redis différente pour les tests
        return RedisSettings(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, database=1
        )

    # En production/développement, utilise l'URL Redis configurée
    redis_url = settings.redis_url
    if redis_url and redis_url.startswith("redis"):
        return RedisSettings.from_dsn(redis_url)

    # Fallback si l'URL n'est pas valide
    return RedisSettings(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        database=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD or None,
    )


class WorkerSettings:
    """
    Configuration pour le worker Arq.
    """

    functions = [send_webhook]
    redis_settings = get_redis_settings()
    job_timeout = 60  # 1 minute
    max_jobs = 10
    keep_result = 3600  # 1 heure


# Pool de connexions Arq qui sera utilisé par l'application pour enqueuer les tâches
arq_pool = None


async def startup(ctx: Dict[str, Any]) -> None:
    global arq_pool
    arq_pool = await create_pool(WorkerSettings)


async def shutdown(ctx: Dict[str, Any]) -> None:
    if arq_pool:
        await arq_pool.close()
