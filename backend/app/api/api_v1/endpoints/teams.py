"""
Endpoints pour la gestion des équipes.

Ce module contient les endpoints pour gérer les équipes, y compris la création,
la lecture, la mise à jour et la suppression des équipes, ainsi que la gestion
des membres d'équipe.
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app import models, schemas
from app.api import deps
from app.db.session import get_db
from app.models.team import Team
from app.schemas.team import TeamCreate, TeamUpdate, Team as TeamSchema

router = APIRouter()


@router.get("/", response_model=List[TeamSchema])
async def read_teams(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Récupère une liste paginée des équipes auxquelles l'utilisateur appartient.
    """
    # Récupérer les équipes où l'utilisateur est membre ou propriétaire
    stmt = (
        select(Team)
        .where((Team.owner_id == current_user.id) | (Team.members.any(id=current_user.id)))
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(stmt)
    teams = result.scalars().all()
    return teams


@router.post("/", response_model=TeamSchema, status_code=status.HTTP_201_CREATED)
async def create_team(
    *,
    db: AsyncSession = Depends(get_db),
    team_in: TeamCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Crée une nouvelle équipe.
    """
    team = Team(
        name=team_in.name,
        description=team_in.description,
        is_public=team_in.is_public,
        owner_id=current_user.id,
    )

    db.add(team)
    await db.commit()
    await db.refresh(team)

    return team


@router.get("/{team_id}", response_model=TeamSchema)
async def read_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Récupère une équipe par son ID.
    """
    stmt = select(Team).options(selectinload(Team.owner), selectinload(Team.members)).where(Team.id == team_id)
    result = await db.execute(stmt)
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipe non trouvée",
        )

    # Vérifier que l'utilisateur a accès à l'équipe
    if not (team.owner_id == current_user.id or current_user in team.members):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas la permission d'accéder à cette équipe",
        )

    return team


@router.put("/{team_id}", response_model=TeamSchema)
async def update_team(
    *,
    db: AsyncSession = Depends(get_db),
    team_id: int,
    team_in: TeamUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Met à jour une équipe.
    """
    stmt = select(Team).where(Team.id == team_id)
    result = await db.execute(stmt)
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipe non trouvée",
        )

    # Vérifier que l'utilisateur est le propriétaire de l'équipe
    if team.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul le propriétaire peut modifier cette équipe",
        )

    # Mettre à jour les champs fournis
    update_data = team_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(team, field, value)

    await db.commit()
    await db.refresh(team)

    return team


@router.delete("/{team_id}", response_model=schemas.Msg)
async def delete_team(
    *,
    db: AsyncSession = Depends(get_db),
    team_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Supprime une équipe.
    """
    stmt = select(Team).where(Team.id == team_id)
    result = await db.execute(stmt)
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipe non trouvée",
        )

    # Vérifier que l'utilisateur est le propriétaire de l'équipe ou un superutilisateur
    if team.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul le propriétaire peut supprimer cette équipe",
        )

    await db.delete(team)
    await db.commit()

    return {"msg": "Équipe supprimée avec succès"}


@router.get("/{team_id}/public", response_model=List[schemas.Composition])
async def get_public_compositions(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Récupère les compositions publiques d'une équipe.
    """
    from app.models import Composition

    stmt = (
        select(Composition)
        .where((Composition.team_id == team_id) & (Composition.is_public == True))  # noqa: E712
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(stmt)
    compositions = result.scalars().all()

    return compositions


@router.get("/{team_id}/members", response_model=List[schemas.User])
async def get_team_members(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Récupère les membres d'une équipe.
    """
    # Vérifier que l'utilisateur a accès à l'équipe
    stmt = select(Team).where(
        (Team.id == team_id) & ((Team.owner_id == current_user.id) | (Team.members.any(id=current_user.id)))
    )
    result = await db.execute(stmt)
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipe non trouvée ou accès refusé",
        )

    # Charger les membres avec leurs rôles dans l'équipe
    stmt = (
        select(models.User)
        .join(models.team_members, models.User.id == models.team_members.c.user_id)
        .where(models.team_members.c.team_id == team_id)
    )

    result = await db.execute(stmt)
    members = result.scalars().all()

    return members
