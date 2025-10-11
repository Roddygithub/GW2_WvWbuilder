from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.api import deps
from app.models import User
from app.schemas.webhook import Webhook, WebhookCreate, WebhookUpdate

router = APIRouter()


@router.post(
    "/",
    response_model=Webhook,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouveau webhook",
    description="Crée un nouveau webhook pour l'utilisateur authentifié.",
)
async def create_webhook(
    webhook_in: WebhookCreate,
    current_user: User = Depends(deps.get_current_active_user),
    webhook_service: deps.WebhookService = Depends(deps.get_webhook_service),
):
    """
    Crée un webhook pour recevoir des notifications sur des événements spécifiques.
    Le secret du webhook sera généré automatiquement et ne sera visible qu'une seule fois.
    """
    webhook = await webhook_service.create_webhook(webhook_in=webhook_in, user_id=current_user.id)
    return webhook


@router.get(
    "/",
    response_model=List[Webhook],
    summary="Lister les webhooks de l'utilisateur",
    description="Récupère la liste de tous les webhooks créés par l'utilisateur authentifié.",
)
async def read_webhooks(
    current_user: User = Depends(deps.get_current_active_user),
    webhook_service: deps.WebhookService = Depends(deps.get_webhook_service),
    skip: int = 0,
    limit: int = 100,
):
    """
    Récupère les webhooks de l'utilisateur.
    """
    webhooks = await webhook_service.get_webhooks(user_id=current_user.id, skip=skip, limit=limit)
    return webhooks


@router.get(
    "/{webhook_id}",
    response_model=Webhook,
    summary="Récupérer un webhook spécifique",
    description="Récupère les détails d'un webhook par son ID.",
)
async def read_webhook(
    webhook_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    webhook_service: deps.WebhookService = Depends(deps.get_webhook_service),
):
    """
    Récupère un webhook par son ID.
    L'utilisateur doit être le propriétaire du webhook.
    """
    webhook = await webhook_service.get_webhook(webhook_id=webhook_id, user_id=current_user.id)
    if not webhook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook non trouvé")
    return webhook


@router.put(
    "/{webhook_id}",
    response_model=Webhook,
    summary="Mettre à jour un webhook",
    description="Met à jour l'URL, les types d'événements ou le statut d'un webhook.",
)
async def update_webhook(
    webhook_id: int,
    webhook_in: WebhookUpdate,
    current_user: User = Depends(deps.get_current_active_user),
    webhook_service: deps.WebhookService = Depends(deps.get_webhook_service),
):
    """
    Met à jour un webhook existant.
    Seuls les champs fournis dans le corps de la requête seront mis à jour.
    """
    # Get the webhook first to check ownership
    webhook = await webhook_service.get_webhook(webhook_id=webhook_id, user_id=current_user.id)
    if not webhook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook non trouvé")

    # Update the webhook
    updated_webhook = await webhook_service.update_webhook(
        webhook_id=webhook_id, webhook_in=webhook_in, user_id=current_user.id
    )

    if not updated_webhook:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Échec de la mise à jour du webhook"
        )

    return updated_webhook


@router.delete(
    "/{webhook_id}",
    summary="Supprimer un webhook",
    description="Supprime un webhook par son ID.",
)
async def delete_webhook(
    webhook_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    webhook_service: deps.WebhookService = Depends(deps.get_webhook_service),
):
    """
    Supprime un webhook.
    L'utilisateur doit être le propriétaire du webhook pour le supprimer.
    """
    # Get the webhook first to check ownership
    webhook = await webhook_service.get_webhook(webhook_id=webhook_id, user_id=current_user.id)
    if not webhook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook non trouvé")

    # Delete the webhook
    deleted_webhook = await webhook_service.delete_webhook(webhook_id=webhook_id, user_id=current_user.id)

    if not deleted_webhook:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Échec de la suppression du webhook"
        )

    return deleted_webhook
