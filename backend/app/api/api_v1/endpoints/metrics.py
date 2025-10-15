"""
Endpoints pour la surveillance des métriques de la base de données.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, List, Any
from datetime import datetime

from app.core.config import settings
from app.core.security import get_current_active_user
from app.models.user import User
from app.core import db_monitor

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


@router.get("/db/metrics", response_model=List[Dict[str, Any]])
async def get_db_metrics(
    limit: int = 10, current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """
    Récupère les métriques historiques de la base de données.

    Args:
        limit: Nombre maximum de métriques à retourner (par défaut: 10)
        current_user: Utilisateur authentifié

    Returns:
        Liste des métriques de la base de données
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Vous n'avez pas les autorisations nécessaires pour accéder à ces métriques",
        )

    # Limiter le nombre de métriques retournées
    metrics = [m.to_dict() for m in db_monitor.metrics_history[-limit:]]
    return metrics


@router.get("/db/issues", response_model=List[Dict[str, Any]])
async def get_db_issues(
    current_user: User = Depends(get_current_active_user),
) -> List[Dict[str, Any]]:
    """
    Vérifie les problèmes potentiels dans la base de données.

    Args:
        current_user: Utilisateur authentifié

    Returns:
        Liste des problèmes détectés dans la base de données
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Vous n'avez pas les autorisations nécessaires pour accéder à ces informations",
        )

    return await db_monitor.check_for_issues()


@router.get("/db/status", response_model=Dict[str, Any])
async def get_db_status(
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Récupère l'état actuel de la base de données.

    Args:
        current_user: Utilisateur authentifié

    Returns:
        État actuel de la base de données
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Vous n'avez pas les autorisations nécessaires pour accéder à ces informations",
        )

    # Récupérer les métriques les plus récentes
    latest_metrics = (
        db_monitor.metrics_history[-1] if db_monitor.metrics_history else None
    )

    # Vérifier les problèmes actuels
    issues = await db_monitor.check_for_issues()

    return {
        "status": "ok" if not issues else "warning",
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": latest_metrics.to_dict() if latest_metrics else {},
        "issues": issues,
    }
