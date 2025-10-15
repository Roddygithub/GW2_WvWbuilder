"""
CRUD operations for EliteSpecialization model with optimized loading and caching.
"""

from typing import Any, Dict, List, Optional, Union

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models import EliteSpecialization, Profession
from app.schemas.elite_specialization import (
    EliteSpecializationCreate,
    EliteSpecializationUpdate,
    GameMode,
)
from app.core.cache import cache
from app.core.config import settings


class CRUDEliteSpecialization(
    CRUDBase[EliteSpecialization, EliteSpecializationCreate, EliteSpecializationUpdate]
):
    """
    CRUD operations for EliteSpecialization model with optimized loading and caching.
    """

    async def get(
        self, db: AsyncSession, id: Any, load_relations: bool = False
    ) -> Optional[EliteSpecialization]:
        """
        Get an elite specialization by ID with optional relation loading.

        Args:
            db: Async database session
            id: ID of the elite specialization
            load_relations: If True, loads related models (profession, builds, etc.)

        Returns:
            Optional[EliteSpecialization]: The elite specialization if found, None otherwise
        """
        cache_key = f"elite_spec:{id}"

        # Try to get from cache first
        if settings.CACHE_ENABLED and not load_relations:
            cached_elite_spec = await cache.get(cache_key)
            if cached_elite_spec is not None:
                return cached_elite_spec

        # Build the base query
        query = select(EliteSpecialization).where(EliteSpecialization.id == id)

        # Load relations if requested
        if load_relations:
            query = query.options(
                selectinload(EliteSpecialization.profession).selectinload(
                    Profession.elite_specializations
                ),
                selectinload(EliteSpecialization.builds),
            )

        # Execute query
        result = await db.execute(query)
        elite_spec = result.scalars().first()

        # Cache the result if not loading relations
        if settings.CACHE_ENABLED and not load_relations and elite_spec:
            await cache.set(cache_key, elite_spec, ttl=settings.CACHE_TTL)

        return elite_spec

    async def get_by_name(
        self, db: AsyncSession, *, name: str, load_relations: bool = False
    ) -> Optional[EliteSpecialization]:
        """
        Get an elite specialization by name with optional relation loading.

        Args:
            db: Async database session
            name: Name of the elite specialization (case-insensitive)
            load_relations: If True, loads related models (profession, builds, etc.)

        Returns:
            Optional[EliteSpecialization]: The elite specialization if found, None otherwise
        """
        cache_key = f"elite_spec:name:{name.lower()}"

        # Try to get from cache first
        if settings.CACHE_ENABLED and not load_relations:
            cached_elite_spec = await cache.get(cache_key)
            if cached_elite_spec is not None:
                return cached_elite_spec

        # Build the base query
        query = select(EliteSpecialization).where(
            func.lower(EliteSpecialization.name) == name.lower()
        )

        # Load relations if requested
        if load_relations:
            query = query.options(
                selectinload(EliteSpecialization.profession).selectinload(
                    Profession.elite_specializations
                ),
                selectinload(EliteSpecialization.builds),
            )

        # Execute query
        result = await db.execute(query)
        elite_spec = result.scalars().first()

        # Cache the result if not loading relations
        if settings.CACHE_ENABLED and not load_relations and elite_spec:
            await cache.set(cache_key, elite_spec, ttl=settings.CACHE_TTL)

        return elite_spec

    async def get_by_profession(
        self, db: AsyncSession, profession_id: int, load_relations: bool = False
    ) -> List[EliteSpecialization]:
        """
        Get all elite specs for a profession with optional relation loading.

        Args:
            db: Async database session
            profession_id: ID of the profession
            load_relations: If True, loads related models (builds, etc.)

        Returns:
            List[EliteSpecialization]: List of elite specializations for the profession
        """
        cache_key = f"profession:{profession_id}:elite_specs"

        # Try to get from cache first
        if settings.CACHE_ENABLED and not load_relations:
            cached_elite_specs = await cache.get(cache_key)
            if cached_elite_specs is not None:
                return cached_elite_specs

        # Build the base query
        query = (
            select(EliteSpecialization)
            .where(EliteSpecialization.profession_id == profession_id)
            .order_by(EliteSpecialization.id)
        )

        # Load relations if requested
        if load_relations:
            query = query.options(selectinload(EliteSpecialization.builds))

        # Execute query
        result = await db.execute(query)
        elite_specs = result.scalars().all()

        # Cache the result if not loading relations
        if settings.CACHE_ENABLED and not load_relations:
            await cache.set(cache_key, elite_specs, ttl=settings.CACHE_TTL)

        return elite_specs

    async def get_viable_for_game_mode(
        self,
        db: AsyncSession,
        game_mode: GameMode,
        profession_id: Optional[int] = None,
        load_relations: bool = False,
    ) -> List[EliteSpecialization]:
        """
        Get elite specs viable for a specific game mode with optional relation loading.

        Args:
            db: Async database session
            game_mode: The game mode to check viability for
            profession_id: Optional ID of the profession to filter by
            load_relations: If True, loads related models (profession, builds, etc.)

        Returns:
            List[EliteSpecialization]: List of viable elite specializations
        """
        cache_key = f"elite_specs:game_mode:{game_mode.value}"
        if profession_id:
            cache_key += f":profession:{profession_id}"

        # Try to get from cache first
        if settings.CACHE_ENABLED and not load_relations:
            cached_elite_specs = await cache.get(cache_key)
            if cached_elite_specs is not None:
                return cached_elite_specs

        # Build the base query
        query = select(EliteSpecialization).where(
            EliteSpecialization.game_mode_affinity.contains([game_mode.value])
        )

        # Filter by profession if specified
        if profession_id:
            query = query.where(EliteSpecialization.profession_id == profession_id)

        # Order the results
        query = query.order_by(EliteSpecialization.id)

        # Load relations if requested
        if load_relations:
            query = query.options(
                selectinload(EliteSpecialization.profession),
                selectinload(EliteSpecialization.builds),
            )

        # Execute query
        result = await db.execute(query)
        elite_specs = result.scalars().all()

        # Cache the result if not loading relations
        if settings.CACHE_ENABLED and not load_relations:
            await cache.set(cache_key, elite_specs, ttl=settings.CACHE_TTL)

        return elite_specs
        return result.scalars().all()

    async def create(
        self, db: AsyncSession, *, obj_in: EliteSpecializationCreate
    ) -> EliteSpecialization:
        """
        Create a new elite specialization and invalidate related caches.

        Args:
            db: Async database session
            obj_in: Elite specialization creation data

        Returns:
            EliteSpecialization: The created elite specialization
        """
        db_obj = EliteSpecialization(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        # Invalidate related caches
        await self.invalidate_cache(db, db_obj.id, db_obj.profession_id, db_obj.name)

        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: EliteSpecialization,
        obj_in: Union[EliteSpecializationUpdate, Dict[str, Any]],
    ) -> EliteSpecialization:
        """
        Update an elite specialization and invalidate related caches.

        Args:
            db: Async database session
            db_obj: The elite specialization to update
            obj_in: The update data

        Returns:
            EliteSpecialization: The updated elite specialization
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        # Store old values for cache invalidation
        old_profession_id = db_obj.profession_id
        old_name = db_obj.name

        # Update the elite specialization
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        # Invalidate caches for both old and new values if they changed
        profession_id = db_obj.profession_id

        if profession_id != old_profession_id or "profession_id" in update_data:
            # Invalidate caches for old profession
            await self.invalidate_cache(db, db_obj.id, old_profession_id, old_name)

        # Invalidate caches for new values
        await self.invalidate_cache(db, db_obj.id, profession_id, db_obj.name)

        return db_obj

    async def remove(
        self, db: AsyncSession, *, id: int
    ) -> Optional[EliteSpecialization]:
        """
        Remove an elite specialization and invalidate related caches.

        Args:
            db: Async database session
            id: ID of the elite specialization to remove

        Returns:
            Optional[EliteSpecialization]: The removed elite specialization if it existed, None otherwise
        """
        elite_spec = await self.get(db, id=id)
        if not elite_spec:
            return None

        # Store values for cache invalidation
        profession_id = elite_spec.profession_id
        elite_spec_name = elite_spec.name

        # Invalidate caches before deletion
        await self.invalidate_cache(db, id, profession_id, elite_spec_name)

        await db.delete(elite_spec)
        await db.commit()
        return elite_spec

    async def invalidate_cache(
        self,
        db: AsyncSession,
        elite_spec_id: Optional[int] = None,
        profession_id: Optional[int] = None,
        elite_spec_name: Optional[str] = None,
    ) -> None:
        """
        Invalidate cache for elite specialization and related data.

        Args:
            db: Async database session
            elite_spec_id: Optional ID of the elite specialization
            profession_id: Optional ID of the profession
            elite_spec_name: Optional name of the elite specialization (for cache invalidation by name)
        """
        if not settings.CACHE_ENABLED:
            return

        # Invalidate specific elite spec caches
        if elite_spec_id:
            await cache.delete(f"elite_spec:{elite_spec_id}")

        if elite_spec_name:
            await cache.delete(f"elite_spec:name:{elite_spec_name.lower()}")

        # Invalidate profession's elite specs cache
        if profession_id:
            await cache.delete(f"profession:{profession_id}:elite_specs")

            # Also invalidate the profession cache as elite specs are often included
            profession = await db.get(Profession, profession_id)
            if profession:
                await cache.delete(f"profession:{profession_id}")

        # Invalidate game mode caches
        if elite_spec_id:
            # Get the elite spec to check its game modes
            elite_spec = await self.get(db, elite_spec_id)
            if elite_spec and elite_spec.game_mode_affinity:
                for game_mode in elite_spec.game_mode_affinity:
                    await cache.delete(f"elite_specs:game_mode:{game_mode}")
                    if profession_id:
                        await cache.delete(
                            f"elite_specs:game_mode:{game_mode}:profession:{profession_id}"
                        )

        # Invalidate builds that use this elite spec
        if elite_spec_id:
            await cache.delete(f"builds:elite_spec:{elite_spec_id}:*")


# Create an instance of CRUDEliteSpecialization to be imported and used in other modules
elite_specialization = CRUDEliteSpecialization(EliteSpecialization)
