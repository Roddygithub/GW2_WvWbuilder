"""
Schémas Pydantic pour la gestion des membres d'équipe.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, validator

from app.schemas.user import User
from app.models.enums import TeamRole


class TeamMemberBase(BaseModel):
    """Schéma de base pour un membre d'équipe."""
    role: TeamRole = Field(
        default=TeamRole.MEMBER, 
        description="Rôle du membre dans l'équipe"
    )
    is_admin: bool = Field(
        default=False,
        description="Indique si le membre est administrateur de l'équipe"
    )


class TeamMemberCreate(TeamMemberBase):
    """Schéma pour l'ajout d'un membre à une équipe."""
    user_id: int = Field(..., description="ID de l'utilisateur à ajouter")


class TeamMemberUpdate(TeamMemberBase):
    """Schéma pour la mise à jour du rôle d'un membre."""
    role: Optional[TeamRole] = Field(
        None,
        description="Nouveau rôle du membre dans l'équipe"
    )
    is_admin: Optional[bool] = Field(
        None,
        description="Indique si le membre est administrateur de l'équipe"
    )


class TeamMember(TeamMemberBase):
    """Schéma pour un membre d'équipe avec les détails de l'utilisateur."""
    user: User = Field(..., description="Détails de l'utilisateur")
    joined_at: datetime = Field(..., description="Date d'ajout à l'équipe")
    left_at: Optional[datetime] = Field(
        None, 
        description="Date de départ de l'équipe"
    )
    is_active: bool = Field(..., description="Indique si le membre est actif")

    class Config:
        from_attributes = True  # Remplacé orm_mode pour la compatibilité Pydantic v2


# Schéma pour la réponse de l'API
class TeamMemberResponse(BaseModel):
    """Schéma de réponse pour les opérations sur les membres d'équipe."""
    success: bool = Field(..., description="Indique si l'opération a réussi")
    message: str = Field(..., description="Message détaillé")
    member: Optional[TeamMember] = Field(
        None, 
        description="Membre concerné"
    )

    class Config:
        json_schema_extra = {  # Remplacé schema_extra pour la compatibilité Pydantic v2
            "example": {
                "success": True,
                "message": "Membre ajouté avec succès",
                "member": {
                    "user": {
                        "id": 2,
                        "email": "membre@example.com",
                        "username": "membre1",
                        "is_active": True,
                        "is_superuser": False
                    },
                    "role": "MEMBER",
                    "is_admin": False,
                    "joined_at": "2023-01-01T00:00:00",
                    "left_at": None,
                    "is_active": True
                }
            }
        }
