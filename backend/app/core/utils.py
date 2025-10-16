"""
Utilitaires généraux pour l'application.
"""

import secrets
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Type, TypeVar

from fastapi import Request
from sqlalchemy.orm import Session

from app.db.base_class import Base

# Type variable for SQLAlchemy models
ModelType = TypeVar("ModelType", bound=Base)


def generate_secret_key(length: int = 32) -> str:
    """Génère une clé secrète aléatoire.

    Args:
        length: Longueur de la clé en octets (par défaut: 32)

    Returns:
        Une chaîne hexadécimale de longueur `length * 2`
    """
    return secrets.token_hex(length)


def generate_unique_id() -> str:
    """Génère un identifiant unique basé sur le timestamp."""
    return str(int(datetime.now(timezone.utc).timestamp() * 1000))


def to_camel_case(snake_str: str) -> str:
    """Convertit une chaîne snake_case en camelCase."""
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def to_snake_case(camel_str: str) -> str:
    """Convertit une chaîne camelCase en snake_case."""
    return "".join(["_" + c.lower() if c.isupper() else c for c in camel_str]).lstrip(
        "_"
    )


def get_pagination_links(
    request: Request, page: int, total_pages: int, page_size: int, total_items: int
) -> Dict[str, Optional[str]]:
    """
    Génère les liens de pagination pour une réponse API.

    Args:
        request: Requête HTTP actuelle
        page: Page actuelle
        total_pages: Nombre total de pages
        page_size: Nombre d'éléments par page
        total_items: Nombre total d'éléments

    Returns:
        Dict avec les liens de pagination (first, prev, next, last)
    """
    base_url = str(request.url).split("?")[0]
    query_params = dict(request.query_params)

    def build_url(p: int) -> str:
        params = query_params.copy()
        params["page"] = p
        params["size"] = page_size
        return f"{base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"

    return {
        "first": build_url(1) if page > 1 else None,
        "prev": build_url(page - 1) if page > 1 else None,
        "next": build_url(page + 1) if page < total_pages else None,
        "last": build_url(total_pages) if page < total_pages else None,
        "total_pages": total_pages,
        "total_items": total_items,
        "current_page": page,
        "page_size": page_size,
    }


def get_or_create(
    db: Session,
    model: Type[ModelType],
    defaults: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> tuple[ModelType, bool]:
    """
    Récupère un objet ou le crée s'il n'existe pas.

    Args:
        db: Session de base de données
        model: Classe du modèle SQLAlchemy
        defaults: Valeurs par défaut pour la création
        **kwargs: Critères de recherche

    Returns:
        Tuple (objet, created) où created est un booléen indiquant si l'objet a été créé
    """
    instance = db.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = defaults or {}
        params.update(kwargs)
        instance = model(**params)
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return instance, True


def log_error(
    error: Exception,
    message: str = "An error occurred",
    extra: Optional[Dict[str, Any]] = None,
    level: str = "error",
) -> None:
    """
    Enregistre une erreur avec des informations de contexte.

    Args:
        error: L'exception qui a été levée
        message: Message d'erreur personnalisé
        extra: Informations supplémentaires à enregistrer
        level: Niveau de log (error, warning, info, etc.)
    """
    log_data = {
        "message": str(error),
        "error_type": error.__class__.__name__,
        "request_id": request_id_var.get(),
        "extra": extra or {},
    }

    if hasattr(error, "__traceback__"):
        import traceback

        log_data["traceback"] = "".join(traceback.format_tb(error.__traceback__))

    logger_method = getattr(logger, level.lower(), logger.error)
    logger_method(message, extra={"error": log_data})
