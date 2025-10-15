"""
Module de gestion de la pagination pour les requêtes SQLAlchemy.
"""

from typing import Any, Dict, Generic, List, TypeVar

from fastapi import Query
from pydantic import BaseModel
from pydantic.generics import GenericModel
from sqlalchemy.orm import Query as SQLAlchemyQuery

# Type variable for the model
ModelType = TypeVar("ModelType")


class PaginationParams(BaseModel):
    """Paramètres de pagination pour les requêtes."""

    page: int = Query(1, ge=1, description="Numéro de page")
    size: int = Query(20, ge=1, le=100, description="Nombre d'éléments par page")

    @property
    def offset(self) -> int:
        """Calcule l'offset pour la requête SQL."""
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        """Retourne la taille de la page."""
        return self.size


class PaginatedResponse(GenericModel, Generic[ModelType]):
    """Modèle de réponse paginée."""

    items: List[ModelType]
    total: int
    page: int
    size: int
    pages: int

    class Config:
        json_encoders = {}
        orm_mode = True


def paginate(
    query: SQLAlchemyQuery[ModelType], pagination: PaginationParams
) -> SQLAlchemyQuery[ModelType]:
    """
    Applique la pagination à une requête SQLAlchemy.

    Args:
        query: Requête SQLAlchemy à paginer
        pagination: Paramètres de pagination

    Returns:
        La requête paginée
    """
    return query.offset(pagination.offset).limit(pagination.limit)


def create_paginated_response(
    items: List[ModelType], total: int, pagination: PaginationParams
) -> Dict[str, Any]:
    """
    Crée une réponse paginée standardisée.

    Args:
        items: Liste des éléments de la page courante
        total: Nombre total d'éléments
        pagination: Paramètres de pagination

    Returns:
        Un dictionnaire contenant la réponse paginée
    """
    return {
        "items": items,
        "total": total,
        "page": pagination.page,
        "size": pagination.size,
        "pages": (total + pagination.size - 1) // pagination.size,
    }
