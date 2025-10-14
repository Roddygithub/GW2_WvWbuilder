"""
Schémas Pydantic pour la gestion des tags.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class TagBase(BaseModel):
    """Schéma de base pour un tag."""

    name: str = Field(..., max_length=50, description="Nom du tag")
    description: Optional[str] = Field(None, max_length=255, description="Description du tag")


class TagCreate(TagBase):
    """Schéma pour la création d'un tag."""

    pass


class TagUpdate(TagBase):
    """Schéma pour la mise à jour d'un tag."""

    name: Optional[str] = Field(None, max_length=50, description="Nom du tag")
    description: Optional[str] = Field(None, max_length=255, description="Description du tag")


class TagInDBBase(TagBase):
    """Schéma de base pour un tag en base de données."""

    id: int = Field(..., description="ID du tag")
    created_at: datetime = Field(..., description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    model_config = ConfigDict(from_attributes=True)


class TagStats(TagInDBBase):
    """
    Schéma pour les statistiques d'utilisation d'un tag.
    Inclut le nombre d'utilisations du tag.
    """

    usage_count: int = Field(0, description="Nombre d'utilisations du tag")

    model_config = ConfigDict(from_attributes=True)


class Tag(TagInDBBase):
    """Schéma complet d'un tag."""

    pass


# Schéma pour la réponse de l'API
class TagResponse(BaseModel):
    """Schéma de réponse pour les opérations sur les tags."""

    success: bool = Field(..., description="Indique si l'opération a réussi")
    message: str = Field(..., description="Message détaillé")
    tag: Optional[Tag] = Field(None, description="Tag concerné")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Opération réussie",
                "tag": {
                    "id": 1,
                    "name": "WvW",
                    "description": "Pour les builds orientés Monde contre Monde",
                    "created_at": "2023-01-01T00:00:00",
                    "updated_at": "2023-01-01T00:00:00",
                },
            }
        }
    )
