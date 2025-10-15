"""
Endpoints pour la gestion des tags et des statistiques.

Ce module contient les endpoints pour gérer les tags et récupérer des statistiques.
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.api import deps
from app.db.session import get_db
from app.models.tag import Tag
from app.models.composition_tag import CompositionTag
from app.schemas.tag import TagStats

router = APIRouter()


@router.get("/stats/most-used", response_model=List[TagStats])
async def get_most_used_tags(
    *,
    db: AsyncSession = Depends(get_db),
    limit: int = 10,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Récupère les tags les plus utilisés avec leur nombre d'utilisations.
    """
    # Requête pour compter le nombre d'utilisations de chaque tag
    stmt = (
        select(
            Tag.id,
            Tag.name,
            Tag.description,
            func.count(CompositionTag.tag_id).label("usage_count"),
        )
        .join(CompositionTag, Tag.id == CompositionTag.tag_id, isouter=True)
        .group_by(Tag.id)
        .order_by(func.count(CompositionTag.tag_id).desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    tags_with_usage = result.all()

    # Convertir les résultats en objets Pydantic
    return [
        TagStats(
            id=tag.id,
            name=tag.name,
            description=tag.description,
            usage_count=tag.usage_count or 0,
        )
        for tag in tags_with_usage
    ]


@router.get("/", response_model=List[schemas.Tag])
async def read_tags(
    *,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Récupère une liste paginée de tous les tags.
    """
    stmt = select(Tag).offset(skip).limit(limit)
    result = await db.execute(stmt)
    tags = result.scalars().all()
    return tags


@router.get("/{tag_id}", response_model=schemas.Tag)
async def read_tag(
    *,
    db: AsyncSession = Depends(get_db),
    tag_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Récupère un tag par son ID.
    """
    stmt = select(Tag).where(Tag.id == tag_id)
    result = await db.execute(stmt)
    tag = result.scalar_one_or_none()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag non trouvé",
        )

    return tag


@router.post("/", response_model=schemas.Tag, status_code=status.HTTP_201_CREATED)
async def create_tag(
    *,
    db: AsyncSession = Depends(get_db),
    tag_in: schemas.TagCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Crée un nouveau tag. Nécessite des privilèges d'administrateur.
    """
    # Vérifier si un tag avec le même nom existe déjà
    stmt = select(Tag).where(Tag.name == tag_in.name)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un tag avec ce nom existe déjà",
        )

    tag = Tag(**tag_in.dict())
    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    return tag


@router.put("/{tag_id}", response_model=schemas.Tag)
async def update_tag(
    *,
    db: AsyncSession = Depends(get_db),
    tag_id: int,
    tag_in: schemas.TagUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Met à jour un tag. Nécessite des privilèges d'administrateur.
    """
    stmt = select(Tag).where(Tag.id == tag_id)
    result = await db.execute(stmt)
    tag = result.scalar_one_or_none()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag non trouvé",
        )

    # Vérifier si un autre tag avec le même nom existe déjà
    if tag_in.name and tag_in.name != tag.name:
        stmt = select(Tag).where(Tag.name == tag_in.name, Tag.id != tag_id)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un autre tag avec ce nom existe déjà",
            )

    # Mettre à jour les champs fournis
    update_data = tag_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tag, field, value)

    await db.commit()
    await db.refresh(tag)

    return tag


@router.delete("/{tag_id}", response_model=schemas.Msg)
async def delete_tag(
    *,
    db: AsyncSession = Depends(get_db),
    tag_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Supprime un tag. Nécessite des privilèges d'administrateur.
    """
    stmt = select(Tag).where(Tag.id == tag_id)
    result = await db.execute(stmt)
    tag = result.scalar_one_or_none()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag non trouvé",
        )

    # Vérifier si le tag est utilisé dans des compositions
    stmt = select(CompositionTag).where(CompositionTag.tag_id == tag_id).limit(1)
    result = await db.execute(stmt)
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de supprimer un tag utilisé dans des compositions",
        )

    await db.delete(tag)
    await db.commit()

    return {"msg": "Tag supprimé avec succès"}
