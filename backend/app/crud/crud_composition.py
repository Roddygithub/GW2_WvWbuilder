"""
CRUD operations for Composition model.

This module provides CRUD operations for the Composition model.
"""

from typing import Any, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models import Composition, User, CompositionTag, Build
from app.models.enums import CompositionRole
from app.schemas.composition import CompositionCreate, CompositionUpdate
from app.core.cache import cache
from app.core.config import settings


class CRUDComposition(CRUDBase[Composition, CompositionCreate, CompositionUpdate]):
    """CRUD operations for Composition model with optimized loading and caching."""

    async def create_with_owner(self, db: AsyncSession, *, obj_in: CompositionCreate, owner_id: int) -> Composition:
        """Create a new composition with an owner."""
        # Extraire les données de l'objet d'entrée
        data = obj_in.dict(exclude_unset=True, exclude={"members"})

        # S'assurer que les champs status et game_mode sont correctement définis
        if "status" not in data:
            data["status"] = "draft"
        if "game_mode" not in data:
            data["game_mode"] = "wvw"

        # Créer l'objet Composition
        db_obj = Composition(
            **data,
            created_by=owner_id,
        )

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_multi_by_owner(
        self, db: AsyncSession, *, owner_id: int, skip: int = 0, limit: int = 100, load_relations: bool = False
    ) -> List[Composition]:
        """
        Get multiple compositions by owner ID with optional relation loading.

        Args:
            db: Async database session
            owner_id: ID of the owner
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (for pagination)
            load_relations: If True, loads related models (tags, builds, team)

        Returns:
            List[Composition]: List of compositions owned by the specified user
        """
        cache_key = f"compositions:owner:{owner_id}:{skip}:{limit}"

        # Try to get from cache first
        if settings.CACHE_ENABLED:
            cached_compositions = await cache.get(cache_key)
            if cached_compositions is not None:
                return cached_compositions

        # Build the base query
        query = (
            select(Composition)
            .where(Composition.created_by == owner_id)
            .order_by(Composition.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )

        # Load relations if requested
        if load_relations:
            query = query.options(
                selectinload(Composition.tags).joinedload(CompositionTag.tag),
                selectinload(Composition.build),
                selectinload(Composition.team),
            )

        # Execute query
        result = await db.execute(query)
        compositions = result.scalars().all()

        # Cache the result
        if settings.CACHE_ENABLED:
            await cache.set(cache_key, compositions, ttl=settings.CACHE_TTL)

        return compositions

    async def get(self, db: AsyncSession, id: Any, load_relations: bool = False) -> Optional[Composition]:
        """
        Get a composition by ID with optional relation loading.

        Args:
            db: Async database session
            id: ID of the composition
            load_relations: If True, loads related models (tags, builds, owner, team)

        Returns:
            Optional[Composition]: The composition if found, None otherwise
        """
        cache_key = f"composition:{id}"

        # Try to get from cache first
        if settings.CACHE_ENABLED and not load_relations:
            cached_composition = await cache.get(cache_key)
            if cached_composition is not None:
                return cached_composition

        # Build the base query
        query = select(Composition).where(Composition.id == id)

        # Load relations if requested
        if load_relations:
            query = query.options(
                selectinload(Composition.tags).joinedload(CompositionTag.tag),
                selectinload(Composition.builds),
                selectinload(Composition.owner),
                selectinload(Composition.team),
            )

        # Execute query
        result = await db.execute(query)
        composition = result.scalars().first()

        # Cache the result if not loading relations
        if settings.CACHE_ENABLED and not load_relations and composition:
            await cache.set(cache_key, composition, ttl=settings.CACHE_TTL)

        return composition

    async def add_member(
        self,
        db: AsyncSession,
        *,
        composition_id: int,
        user: User,
        role: CompositionRole = CompositionRole.HEALER,
        profession_id: Optional[int] = None,
        elite_specialization_id: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> Optional[Composition]:
        """Add a member to a composition."""
        composition = await self.get(db, id=composition_id)
        if not composition:
            return None

        # Add member to composition
        stmt = select(Composition.members).where(Composition.id == composition_id)
        result = await db.execute(stmt)
        members = result.scalars().all()

        if user not in members:
            composition.members.append(user)
            await db.commit()
            await db.refresh(composition)

        return composition

    async def remove_member(self, db: AsyncSession, *, composition_id: int, user_id: int) -> Optional[Composition]:
        """Remove a member from a composition."""
        composition = await self.get(db, id=composition_id)
        if not composition:
            return None

        # Remove member from composition
        stmt = select(Composition.members).where(Composition.id == composition_id)
        result = await db.execute(stmt)
        members = result.scalars().all()

        user_to_remove = next((u for u in members if u.id == user_id), None)
        if user_to_remove:
            composition.members.remove(user_to_remove)
            await db.commit()
            await db.refresh(composition)

        return composition

    async def add_build(self, db: AsyncSession, *, composition_id: int, build: Build) -> Optional[Composition]:
        """Add a build to a composition."""
        composition = await self.get(db, id=composition_id)
        if not composition:
            return None

        composition.build = build
        await db.commit()
        await db.refresh(composition)
        return composition

    async def remove_build(self, db: AsyncSession, *, composition_id: int) -> Optional[Composition]:
        """Remove a build from a composition."""
        composition = await self.get(db, id=composition_id)
        if not composition:
            return None

        composition.build = None
        await db.commit()
        await db.refresh(composition)
        return composition

    async def get_multi_public(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, load_relations: bool = False
    ) -> List[Composition]:
        """
        Get multiple public compositions with optional relation loading.

        Args:
            db: Async database session
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (for pagination)
            load_relations: If True, loads related models (tags, builds, owner, team)

        Returns:
            List[Composition]: List of public compositions
        """
        cache_key = f"compositions:public:{skip}:{limit}"

        # Try to get from cache first
        if settings.CACHE_ENABLED:
            cached_compositions = await cache.get(cache_key)
            if cached_compositions is not None:
                return cached_compositions

        # Build the base query
        query = (
            select(Composition)
            .where(Composition.is_public == True)  # noqa: E712
            .order_by(Composition.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )

        # Load relations if requested
        if load_relations:
            query = query.options(
                selectinload(Composition.tags).joinedload(CompositionTag.tag),
                selectinload(Composition.builds),
                selectinload(Composition.owner),
                selectinload(Composition.team),
            )

        # Execute query
        result = await db.execute(query)
        compositions = result.scalars().all()

        # Cache the result
        if settings.CACHE_ENABLED:
            await cache.set(cache_key, compositions, ttl=settings.CACHE_TTL)

        return compositions

    async def add_tag(self, db: AsyncSession, *, composition_id: int, tag_id: int) -> bool:
        """
        Add a tag to a composition and invalidate related caches.

        Args:
            db: Async database session
            composition_id: ID of the composition
            tag_id: ID of the tag to add

        Returns:
            bool: True if the tag was added, False if it was already associated
        """
        # Check if tag is already associated
        stmt = select(composition_tags).where(
            (composition_tags.c.composition_id == composition_id) & (composition_tags.c.tag_id == tag_id)
        )
        result = await db.execute(stmt)
        if result.first():
            return False  # Tag is already associated

        # Add tag to composition
        stmt = composition_tags.insert().values(composition_id=composition_id, tag_id=tag_id)
        await db.execute(stmt)

        # Invalidate caches
        await self.invalidate_cache(db, composition_id)

        await db.commit()
        return True

    async def remove_tag(self, db: AsyncSession, *, composition_id: int, tag_id: int) -> bool:
        """
        Remove a tag from a composition and invalidate related caches.

        Args:
            db: Async database session
            composition_id: ID of the composition
            tag_id: ID of the tag to remove

        Returns:
            bool: True if the tag was removed, False if it wasn't associated
        """
        # Check if tag is associated
        stmt = select(composition_tags).where(
            (composition_tags.c.composition_id == composition_id) & (composition_tags.c.tag_id == tag_id)
        )
        result = await db.execute(stmt)
        if not result.first():
            return False  # Tag is not associated

        # Remove tag from composition
        stmt = composition_tags.delete().where(
            (composition_tags.c.composition_id == composition_id) & (composition_tags.c.tag_id == tag_id)
        )
        await db.execute(stmt)

        # Invalidate caches
        await self.invalidate_cache(db, composition_id)

        await db.commit()
        return True

    async def invalidate_cache(self, db: AsyncSession, composition_id: int) -> None:
        """
        Invalidate cache for a composition and related data.

        Args:
            db: Async database session
            composition_id: ID of the composition
        """
        if not settings.CACHE_ENABLED:
            return

        # Invalidate composition cache
        await cache.delete(f"composition:{composition_id}")

        # Invalidate composition lists cache
        await cache.delete("compositions:public:*")
        await cache.delete("compositions:owner:*")
        await cache.delete("compositions:team:*")

        # Invalidate related team cache if composition has a team
        composition = await self.get(db, composition_id)
        if composition and composition.team_id:
            await cache.delete(f"team:{composition.team_id}:compositions")


# Create an instance of CRUDComposition to be imported and used in other modules
composition = CRUDComposition(Composition)
