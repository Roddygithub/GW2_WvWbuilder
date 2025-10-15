"""
Endpoints pour la gestion des membres d'équipe.

Ce module contient les endpoints pour gérer les membres d'une équipe,
y compris l'ajout, la suppression et la mise à jour des rôles des membres.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import models, schemas
from app.api import deps
from app.db.session import get_db
from app.models.team import Team
from app.models.team_member import TeamMember
from app.models.user import User
from app.schemas.team import TeamMemberUpdate

router = APIRouter()


@router.post("/{team_id}/members/{user_id}", response_model=schemas.Msg)
async def add_team_member(
    *,
    db: AsyncSession = Depends(get_db),
    team_id: int,
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Ajoute un membre à une équipe.
    """
    # Vérifier que l'équipe existe
    stmt = select(Team).where(Team.id == team_id)
    result = await db.execute(stmt)
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipe non trouvée",
        )

    # Vérifier que l'utilisateur est le propriétaire de l'équipe ou un administrateur
    if team.owner_id != current_user.id and not current_user.is_superuser:
        # Vérifier si l'utilisateur est administrateur de l'équipe
        stmt = select(TeamMember).where(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.user_id == current_user.id,
                TeamMember.is_admin == True,  # noqa: E712
                TeamMember.is_active == True,  # noqa: E712
            )
        )
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seul le propriétaire ou un administrateur peut ajouter des membres",
            )

    # Vérifier que l'utilisateur à ajouter existe
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user_to_add = result.scalar_one_or_none()

    if not user_to_add:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé",
        )

    # Vérifier que l'utilisateur n'est pas déjà membre de l'équipe
    stmt = select(TeamMember).where(
        and_(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
            TeamMember.is_active == True,
        )  # noqa: E712
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'utilisateur est déjà membre de cette équipe",
        )

    # Ajouter l'utilisateur à l'équipe
    team_member = TeamMember(
        team_id=team_id, user_id=user_id, is_admin=False, is_active=True
    )
    db.add(team_member)
    await db.commit()
    await db.refresh(team_member)

    return {"msg": f"Utilisateur {user_to_add.email} ajouté à l'équipe {team.name}"}


@router.put("/{team_id}/members/{user_id}", response_model=schemas.Msg)
async def update_team_member(
    *,
    db: AsyncSession = Depends(get_db),
    team_id: int,
    user_id: int,
    member_in: TeamMemberUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Met à jour le rôle d'un membre d'équipe.
    """
    # Vérifier que l'équipe existe
    stmt = select(Team).where(Team.id == team_id)
    result = await db.execute(stmt)
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipe non trouvée",
        )

    # Vérifier que l'utilisateur est le propriétaire de l'équipe ou un administrateur
    if team.owner_id != current_user.id and not current_user.is_superuser:
        # Vérifier si l'utilisateur est administrateur de l'équipe
        stmt = select(TeamMember).where(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.user_id == current_user.id,
                TeamMember.is_admin == True,  # noqa: E712
                TeamMember.is_active == True,  # noqa: E712
            )
        )
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seul le propriétaire ou un administrateur peut modifier les rôles",
            )

    # Vérifier que l'utilisateur cible est bien membre de l'équipe
    stmt = select(TeamMember).where(
        and_(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
            TeamMember.is_active == True,
        )  # noqa: E712
    )
    result = await db.execute(stmt)
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membre non trouvé dans l'équipe",
        )

    # Mettre à jour le membre
    update_data = member_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(member, field, value)

    db.add(member)
    await db.commit()
    await db.refresh(member)

    return {"msg": "Membre mis à jour avec succès"}


@router.delete("/{team_id}/members/{user_id}", response_model=schemas.Msg)
async def remove_team_member(
    *,
    db: AsyncSession = Depends(get_db),
    team_id: int,
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Supprime un membre d'une équipe.
    """
    # Vérifier que l'équipe existe
    stmt = select(Team).where(Team.id == team_id)
    result = await db.execute(stmt)
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipe non trouvée",
        )

    # Vérifier que l'utilisateur est le propriétaire de l'équipe ou un administrateur
    if team.owner_id != current_user.id and not current_user.is_superuser:
        # Vérifier si l'utilisateur est administrateur de l'équipe
        stmt = select(TeamMember).where(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.user_id == current_user.id,
                TeamMember.is_admin == True,  # noqa: E712
                TeamMember.is_active == True,  # noqa: E712
            )
        )
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seul le propriétaire ou un administrateur peut supprimer des membres",
            )

    # Vérifier que l'utilisateur cible est bien membre de l'équipe
    stmt = select(TeamMember).where(
        and_(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
            TeamMember.is_active == True,
        )  # noqa: E712
    )
    result = await db.execute(stmt)
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membre non trouvé dans l'équipe",
        )

    # Marquer le membre comme inactif au lieu de le supprimer pour conserver l'historique
    member.is_active = False
    member.left_at = datetime.utcnow()

    db.add(member)
    await db.commit()
    await db.refresh(member)

    return {"msg": "Membre retiré de l'équipe avec succès"}
