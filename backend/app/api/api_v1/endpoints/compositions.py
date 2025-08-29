from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy import select, insert, delete
from sqlalchemy.orm import Session

from app.api import deps
from app import models, schemas

router = APIRouter()


def _composition_to_schema(db: Session, comp: models.Composition) -> schemas.Composition:
    # Build members from association table
    members_stmt = (
        select(
            models.models.composition_members.c.user_id,
            models.models.composition_members.c.role_id,
            models.models.composition_members.c.profession_id,
            models.models.composition_members.c.elite_specialization_id,
            models.models.composition_members.c.notes,
        )
        .where(models.models.composition_members.c.composition_id == comp.id)
    )
    members_rows = db.execute(members_stmt).all()
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


def _validate_member_refs(db: Session, m: schemas.CompositionMemberBase | dict) -> None:
    # Support both Pydantic model and plain dict payloads
    getv = (lambda k: m[k]) if isinstance(m, dict) else (lambda k: getattr(m, k))

    user_id = getv("user_id")
    role_id = getv("role_id")
    profession_id = getv("profession_id")
    elite_specialization_id = getv("elite_specialization_id")

    if not db.get(models.User, user_id):
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    if not db.get(models.Role, role_id):
        raise HTTPException(status_code=404, detail=f"Role {role_id} not found")
    prof = db.get(models.Profession, profession_id)
    if not prof:
        raise HTTPException(status_code=404, detail=f"Profession {profession_id} not found")
    if elite_specialization_id is not None:
        elite = db.get(models.EliteSpecialization, elite_specialization_id)
        if not elite:
            raise HTTPException(status_code=404, detail=f"EliteSpecialization {elite_specialization_id} not found")
        # Optional: check elite belongs to profession
        if elite.profession_id != prof.id:
            raise HTTPException(status_code=400, detail="Elite specialization does not belong to the given profession")


def _upsert_members(db: Session, composition_id: int, members: Optional[List[schemas.CompositionMemberBase | dict]]) -> None:
    # Clear existing members then insert new if provided
    db.execute(
        delete(models.models.composition_members).where(
            models.models.composition_members.c.composition_id == composition_id
        )
    )
    if not members:
        return
    for m in members:
        _validate_member_refs(db, m)
        getv = (lambda k: m[k]) if isinstance(m, dict) else (lambda k: getattr(m, k))
        db.execute(
            insert(models.models.composition_members).values(
                composition_id=composition_id,
                user_id=getv("user_id"),
                role_id=getv("role_id"),
                profession_id=getv("profession_id"),
                elite_specialization_id=getv("elite_specialization_id"),
                notes=getv("notes"),
            )
        )


@router.post("/", response_model=schemas.Composition, status_code=201)
def create_composition(
    *,
    db: Session = Depends(deps.get_db),
    composition_in: schemas.CompositionCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    comp = models.Composition(
        name=composition_in.name,
        description=composition_in.description,
        squad_size=composition_in.squad_size,
        is_public=composition_in.is_public,
        created_by=composition_in.created_by or current_user.id,
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)

    # Members insert
    _upsert_members(db, comp.id, composition_in.members)
    db.commit()

    return _composition_to_schema(db, comp)


@router.get("/", response_model=List[schemas.Composition])
def read_compositions(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    is_public: Optional[bool] = Query(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    stmt = select(models.Composition)
    if is_public is not None:
        stmt = stmt.where(models.Composition.is_public == is_public)
    stmt = stmt.offset(skip).limit(limit)
    comps = db.execute(stmt).scalars().all()
    return [_composition_to_schema(db, c) for c in comps]


@router.get("/{composition_id}", response_model=schemas.Composition)
def read_composition(
    composition_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    comp = db.get(models.Composition, composition_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Composition not found")
    if not comp.is_public and not (current_user.is_superuser or comp.created_by == current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return _composition_to_schema(db, comp)


@router.put("/{composition_id}", response_model=schemas.Composition)
def update_composition(
    *,
    composition_id: int,
    composition_in: schemas.CompositionUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    comp = db.get(models.Composition, composition_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Composition not found")
    if not (current_user.is_superuser or comp.created_by == current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    data = composition_in.model_dump(exclude_unset=True)
    members = data.pop("members", None)
    for k, v in data.items():
        setattr(comp, k, v)
    db.add(comp)
    db.commit()
    db.refresh(comp)

    if members is not None:
        # If provided, replace members
        _upsert_members(db, comp.id, members)  # type: ignore[arg-type]
        db.commit()

    return _composition_to_schema(db, comp)


@router.delete("/{composition_id}", status_code=200)
def delete_composition(
    composition_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    comp = db.get(models.Composition, composition_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Composition not found")
    if not (current_user.is_superuser or comp.created_by == current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Remove members first then delete composition
    db.execute(
        delete(models.models.composition_members).where(
            models.models.composition_members.c.composition_id == composition_id
        )
    )
    db.delete(comp)
    db.commit()
    return {"detail": "deleted"}
