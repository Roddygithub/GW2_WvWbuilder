from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, insert, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app import models, schemas

router = APIRouter()


async def _composition_to_schema(db: AsyncSession, comp: models.Composition) -> schemas.Composition:
    # Build members from association table
    members_stmt = select(
        models.models.composition_members.c.user_id,
        models.models.composition_members.c.role_id,
        models.models.composition_members.c.profession_id,
        models.models.composition_members.c.elite_specialization_id,
        models.models.composition_members.c.notes,
    ).where(models.models.composition_members.c.composition_id == comp.id)

    members_rows = await db.execute(members_stmt)
    members: List[Dict[str, Any]] = []

    for r in members_rows:
        members.append(
            {
                "user_id": r.user_id,
                "role_id": r.role_id,
                "profession_id": r.profession_id,
                "elite_specialization_id": r.elite_specialization_id,
                "notes": r.notes,
            }
        )

    members_list = []
    for m in members:
        role = await db.get(models.Role, m["role_id"]) if m["role_id"] else None
        profession = await db.get(models.Profession, m["profession_id"]) if m["profession_id"] else None
        user = await db.get(models.User, m["user_id"]) if m["user_id"] else None
        elite_specialization = (
            await db.get(models.EliteSpecialization, m["elite_specialization_id"])
            if m["elite_specialization_id"]
            else None
        )
        members_list.append(
            {
                "user_id": m["user_id"],
                "role_id": m["role_id"],
                "role_name": role.name if role else None,
                "profession_id": m["profession_id"],
                "profession_name": profession.name if profession else None,
                "elite_specialization_id": m["elite_specialization_id"],
                "elite_specialization_name": elite_specialization.name if elite_specialization else None,
                "notes": m["notes"],
                "user_name": user.username if user else None,
            }
        )

    return schemas.Composition(
        id=comp.id,
        name=comp.name,
        description=comp.description,
        squad_size=comp.squad_size,
        is_public=comp.is_public,
        created_by=comp.created_by,
        created_at=comp.created_at,
        updated_at=comp.updated_at,
        members=members,
        tags=[],
        created_by_username=getattr(comp.creator, "username", None),
    )


async def _validate_member_refs(db: AsyncSession, m: schemas.CompositionMemberBase | dict):
    """
    Validate that all foreign key references in a member exist.
    Returns a dict of the validated member data.
    """
    member_data = m.dict() if hasattr(m, "dict") else m

    # Check role exists if specified
    if "role_id" in member_data and member_data["role_id"] is not None:
        role = await db.get(models.Role, member_data["role_id"])
        if not role:
            raise HTTPException(status_code=400, detail=f"Role with id {member_data['role_id']} not found")

    # Check profession exists if specified
    if "profession_id" in member_data and member_data["profession_id"] is not None:
        profession = await db.get(models.Profession, member_data["profession_id"])
        if not profession:
            raise HTTPException(status_code=400, detail=f"Profession with id {member_data['profession_id']} not found")

    # Check elite spec exists if specified
    if "elite_specialization_id" in member_data and member_data["elite_specialization_id"] is not None:
        elite_spec = await db.get(models.EliteSpecialization, member_data["elite_specialization_id"])
        if not elite_spec:
            raise HTTPException(
                status_code=400,
                detail=f"Elite specialization with id {member_data['elite_specialization_id']} not found",
            )

    return member_data


async def _upsert_members(
    db: AsyncSession,
    composition_id: int,
    members: Optional[List[schemas.CompositionMemberBase | dict]],
) -> None:
    # Clear existing members then insert new if provided
    await db.execute(
        delete(models.models.composition_members).where(
            models.models.composition_members.c.composition_id == composition_id
        )
    )

    if not members:
        await db.commit()
        return

    # Insert new members
    for m in members:
        member_data = m.dict() if hasattr(m, "dict") else m
        member_data["composition_id"] = composition_id
        await db.execute(insert(models.models.composition_members).values(**member_data))


@router.post("/", response_model=schemas.Composition, status_code=201)
async def create_composition(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    composition_in: schemas.CompositionCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new composition.
    """
    # Validate member references
    if composition_in.members:
        for m in composition_in.members:
            await _validate_member_refs(db, m)

    # Create the composition
    composition_data = composition_in.dict(exclude={"members"})
    composition = models.Composition(**composition_data, created_by_id=current_user.id)
    db.add(composition)
    await db.commit()
    await db.refresh(composition)

    # Add members
    if composition_in.members:
        await _upsert_members(db, composition.id, composition_in.members)

    return await _composition_to_schema(db, composition)


@router.get("/", response_model=List[schemas.Composition])
async def read_compositions(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    skip: int = 0,
    limit: int = 100,
    is_public: Optional[bool] = Query(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve compositions with optional filtering by visibility.
    """
    query = select(models.Composition)

    # Filter by visibility if specified
    if is_public is not None:
        query = query.where(models.Composition.is_public == is_public)

    # Only show private compositions to their owners or admins
    if not current_user.is_superuser:
        query = query.where(
            or_(models.Composition.is_public, models.Composition.created_by_id == current_user.id)
        )

    result = await db.execute(query.offset(skip).limit(limit))
    compositions = result.scalars().all()
    return [await _composition_to_schema(db, c) for c in compositions]


@router.get("/{composition_id}", response_model=schemas.Composition)
async def read_composition(
    composition_id: int,
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific composition by ID.
    """
    composition = await db.get(models.Composition, composition_id)
    if not composition:
        raise HTTPException(status_code=404, detail="Composition not found")

    # Check permissions
    if not composition.is_public and composition.created_by_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return await _composition_to_schema(db, composition)


@router.put("/{composition_id}", response_model=schemas.Composition)
async def update_composition(
    *,
    composition_id: int,
    composition_in: schemas.CompositionUpdate,
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a composition.
    """
    composition = await db.get(models.Composition, composition_id)
    if not composition:
        raise HTTPException(status_code=404, detail="Composition not found")

    # Check permissions
    if composition.created_by_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Update composition data
    update_data = composition_in.dict(exclude_unset=True, exclude={"members"})
    for field, value in update_data.items():
        setattr(composition, field, value)

    # Update members if provided
    if composition_in.members is not None:
        for m in composition_in.members:
            await _validate_member_refs(db, m)
        await _upsert_members(db, composition_id, composition_in.members)

    db.add(composition)
    await db.commit()
    await db.refresh(composition)

    return await _composition_to_schema(db, composition)


@router.delete("/{composition_id}", status_code=200)
async def delete_composition(
    composition_id: int,
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a composition.
    """
    composition = await db.get(models.Composition, composition_id)
    if not composition:
        raise HTTPException(status_code=404, detail="Composition not found")

    # Check permissions
    if composition.created_by_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Delete members first
    await db.execute(
        delete(models.models.composition_members).where(
            models.models.composition_members.c.composition_id == composition_id
        )
    )

    # Delete the composition
    await db.delete(composition)
    await db.commit()

    return {"detail": "Composition deleted successfully"}
