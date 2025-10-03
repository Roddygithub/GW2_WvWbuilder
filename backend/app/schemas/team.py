"""
Schémas Pydantic pour la gestion des équipes.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator, ConfigDict

from app.models.enums import TeamRole, TeamStatus
from app.schemas.user import User


class TeamBase(BaseModel):
    """Schéma de base pour une équipe."""
    name: str = Field(..., max_length=100, description="Nom de l'équipe")
    description: Optional[str] = Field(
        None, max_length=500, description="Description de l'équipe"
    )
    status: TeamStatus = Field(
        default=TeamStatus.ACTIVE, description="Statut de l'équipe"
    )
    is_public: bool = Field(
        default=False, 
        description="Indique si l'équipe est visible par tous les utilisateurs"
    )

    model_config = ConfigDict(from_attributes=True)

class TeamCreate(TeamBase):
    """Schéma pour la création d'une équipe."""
    pass


class TeamUpdate(TeamBase):
    """Schéma pour la mise à jour d'une équipe."""
    name: Optional[str] = Field(None, max_length=100, description="Nom de l'équipe")
    description: Optional[str] = Field(
        None, max_length=500, description="Description de l'équipe"
    )
    status: Optional[TeamStatus] = Field(
        None, description="Statut de l'équipe"
    )


class TeamInDBBase(TeamBase):
    """Schéma de base pour une équipe en base de données."""
    id: int = Field(..., description="ID de l'équipe")
    owner_id: int = Field(..., description="ID du propriétaire de l'équipe")
    created_at: datetime = Field(..., description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    model_config = ConfigDict(from_attributes=True)

class TeamMemberBase(BaseModel):
    """Schéma de base pour un membre d'équipe."""
    role: TeamRole = Field(
        default=TeamRole.MEMBER, description="Rôle du membre dans l'équipe"
    )


class TeamMemberCreate(TeamMemberBase):
    """Schéma pour l'ajout d'un membre à une équipe."""
    user_id: int = Field(..., description="ID de l'utilisateur à ajouter")


class TeamMemberUpdate(TeamMemberBase):
    """Schéma pour la mise à jour du rôle d'un membre."""
    role: TeamRole = Field(..., description="Nouveau rôle du membre dans l'équipe")


class TeamMember(TeamMemberBase):
    """Schéma pour un membre d'équipe avec les détails de l'utilisateur."""
    user: User = Field(..., description="Détails de l'utilisateur")
    joined_at: datetime = Field(..., description="Date d'ajout à l'équipe")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour du rôle")

    model_config = ConfigDict(from_attributes=True)

class Team(TeamInDBBase):
    """Schéma complet d'une équipe avec ses membres."""
    members: List[TeamMember] = Field(
        default_factory=list, description="Liste des membres de l'équipe"
    )
    member_count: int = Field(0, description="Nombre de membres dans l'équipe")

    @model_validator(mode='before')
    def set_member_count(cls, values):
        """Calcule automatiquement le nombre de membres."""
        if 'members' in values and values['members'] is not None:
            return len(values['members'])
        return v or 0


# Schéma pour la réponse de l'API
class TeamResponse(BaseModel):
    """Schéma de réponse pour les opérations sur les équipes."""
    success: bool = Field(..., description="Indique si l'opération a réussi")
    message: str = Field(..., description="Message détaillé")
    team: Optional[Team] = Field(None, description="Équipe concernée")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Opération effectuée avec succès",
                "team": {
                    "id": 1,
                    "name": "Mon équipe",
                    "description": "Une équipe de test",
                    "status": "active",
                    "owner_id": 1,
                    "created_at": "2023-01-01T00:00:00",
                    "updated_at": None,
                    "members": [],
                    "member_count": 0
                }
            }
        }
    )
