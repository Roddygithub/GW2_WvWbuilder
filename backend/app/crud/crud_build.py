"""
CRUD operations for Build model with optimized loading and caching.
"""

from typing import Any, Dict, List, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models import Build, Profession, EliteSpecialization
from app.schemas.build import BuildCreate, BuildUpdate
from app.core.cache import cache
from app.core.config import settings


class CRUDBuild(CRUDBase[Build, BuildCreate, BuildUpdate]):
    """
    CRUD operations for Build model with optimized loading and caching.
    """

    async def get(self, db: AsyncSession, id: Any, load_relations: bool = False) -> Optional[Build]:
        """
        Get a build by ID with optional relation loading.

        Args:
            db: Async database session
            id: ID of the build
            load_relations: If True, loads related models (profession, elite spec, etc.)

        Returns:
            Optional[Build]: The build if found, None otherwise
        """
        cache_key = f"build:{id}"

        # Try to get from cache first
        if settings.CACHE_ENABLED and not load_relations:
            cached_build = await cache.get(cache_key)
            if cached_build is not None:
                return cached_build

        # Build the base query
        query = select(Build).where(Build.id == id)

        # Load relations if requested
        if load_relations:
            query = query.options(
                selectinload(Build.profession),
                selectinload(Build.elite_specialization),
                selectinload(Build.created_by_user),
                selectinload(Build.compositions),
            )

        # Execute query
        result = await db.execute(query)
        build = result.scalars().first()

        # Cache the result if not loading relations
        if settings.CACHE_ENABLED and not load_relations and build:
            await cache.set(cache_key, build, ttl=settings.CACHE_TTL)

        return build

    async def get_multi_by_owner(
        self, db: AsyncSession, *, owner_id: int, skip: int = 0, limit: int = 100, load_relations: bool = False
    ) -> List[Build]:
        """
        Get multiple builds by owner ID with optional relation loading.

        Args:
            db: Async database session
            owner_id: ID of the build owner
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (for pagination)
            load_relations: If True, loads related models (profession, elite spec, etc.)

        Returns:
            List[Build]: List of builds for the specified owner
        """
        cache_key = f"builds:owner:{owner_id}:{skip}:{limit}"

        # Try to get from cache first
        if settings.CACHE_ENABLED and not load_relations:
            cached_builds = await cache.get(cache_key)
            if cached_builds is not None:
                return cached_builds

        # Build the base query
        query = (
            select(Build)
            .where(Build.created_by == owner_id)
            .order_by(Build.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )

        # Load relations if requested
        if load_relations:
            query = query.options(
                selectinload(Build.profession),
                selectinload(Build.elite_specialization),
                selectinload(Build.compositions),
            )

        # Execute query
        result = await db.execute(query)
        builds = result.scalars().all()

        # Cache the result if not loading relations
        if settings.CACHE_ENABLED and not load_relations:
            await cache.set(cache_key, builds, ttl=settings.CACHE_TTL)

        return builds

    async def get_multi_by_profession(
        self, db: AsyncSession, *, profession_id: int, skip: int = 0, limit: int = 100, load_relations: bool = False
    ) -> List[Build]:
        """
        Get multiple builds by profession ID with optional relation loading.

        Args:
            db: Async database session
            profession_id: ID of the profession
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (for pagination)
            load_relations: If True, loads related models (profession, elite spec, etc.)

        Returns:
            List[Build]: List of builds for the specified profession
        """
        cache_key = f"builds:profession:{profession_id}:{skip}:{limit}"

        # Try to get from cache first
        if settings.CACHE_ENABLED and not load_relations:
            cached_builds = await cache.get(cache_key)
            if cached_builds is not None:
                return cached_builds

        # Build the base query
        query = (
            select(Build)
            .where(Build.profession_id == profession_id)
            .order_by(Build.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )

        # Load relations if requested
        if load_relations:
            query = query.options(
                selectinload(Build.profession),
                selectinload(Build.elite_specialization),
                selectinload(Build.created_by_user),
            )

        # Execute query
        result = await db.execute(query)
        builds = result.scalars().all()

        # Cache the result if not loading relations
        if settings.CACHE_ENABLED and not load_relations:
            await cache.set(cache_key, builds, ttl=settings.CACHE_TTL)

        return builds

    async def get_multi_by_elite_spec(
        self, db: AsyncSession, *, elite_spec_id: int, skip: int = 0, limit: int = 100, load_relations: bool = False
    ) -> List[Build]:
        """
        Get multiple builds by elite specialization ID with optional relation loading.

        Args:
            db: Async database session
            elite_spec_id: ID of the elite specialization
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (for pagination)
            load_relations: If True, loads related models (profession, elite spec, etc.)

        Returns:
            List[Build]: List of builds for the specified elite specialization
        """
        cache_key = f"builds:elite_spec:{elite_spec_id}:{skip}:{limit}"

        # Try to get from cache first
        if settings.CACHE_ENABLED and not load_relations:
            cached_builds = await cache.get(cache_key)
            if cached_builds is not None:
                return cached_builds

        # Build the base query
        query = (
            select(Build)
            .where(Build.elite_specialization_id == elite_spec_id)
            .order_by(Build.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )

        # Load relations if requested
        if load_relations:
            query = query.options(
                selectinload(Build.profession),
                selectinload(Build.elite_specialization),
                selectinload(Build.created_by_user),
            )

        # Execute query
        result = await db.execute(query)
        builds = result.scalars().all()

        # Cache the result if not loading relations
        if settings.CACHE_ENABLED and not load_relations:
            await cache.set(cache_key, builds, ttl=settings.CACHE_TTL)

        return builds

    async def create(self, db: AsyncSession, *, obj_in: BuildCreate, created_by: int) -> Build:
        """
        Create a new build and invalidate related caches.

        Args:
            db: Async database session
            obj_in: Build creation data
            created_by: ID of the user creating the build

        Returns:
            Build: The created build
        """
        # Convert Pydantic model to dict and add created_by
        db_obj_data = obj_in.dict()
        db_obj_data["created_by"] = created_by

        # Create the build
        db_obj = Build(**db_obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        # Invalidate related caches
        await self.invalidate_cache(
            db, db_obj.id, db_obj.created_by, db_obj.profession_id, db_obj.elite_specialization_id
        )

        return db_obj

    async def update(self, db: AsyncSession, *, db_obj: Build, obj_in: Union[BuildUpdate, Dict[str, Any]]) -> Build:
        """
        Update a build and invalidate related caches.

        Args:
            db: Async database session
            db_obj: The build to update
            obj_in: The update data

        Returns:
            Build: The updated build
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        # Store old values for cache invalidation
        old_profession_id = db_obj.profession_id
        old_elite_spec_id = db_obj.elite_specialization_id

        # Update the build
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        # Invalidate caches for both old and new values if they changed
        profession_id = db_obj.profession_id
        elite_spec_id = db_obj.elite_specialization_id

        if profession_id != old_profession_id or elite_spec_id != old_elite_spec_id:
            # Invalidate caches for old values
            await self.invalidate_cache(db, db_obj.id, db_obj.created_by, old_profession_id, old_elite_spec_id)

        # Invalidate caches for new values
        await self.invalidate_cache(db, db_obj.id, db_obj.created_by, profession_id, elite_spec_id)

        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[Build]:
        """
        Remove a build and invalidate related caches.

        Args:
            db: Async database session
            id: ID of the build to remove

        Returns:
            Optional[Build]: The removed build if it existed, None otherwise
        """
        build = await self.get(db, id=id)
        if not build:
            return None

        # Store values for cache invalidation
        created_by = build.created_by
        profession_id = build.profession_id
        elite_spec_id = build.elite_specialization_id

        # Invalidate caches before deletion
        await self.invalidate_cache(db, id, created_by, profession_id, elite_spec_id)

        await db.delete(build)
        await db.commit()
        return build

    async def invalidate_cache(
        self,
        db: AsyncSession,
        build_id: Optional[int] = None,
        created_by: Optional[int] = None,
        profession_id: Optional[int] = None,
        elite_spec_id: Optional[int] = None,
    ) -> None:
        """
        Invalidate cache for build and related data.

        Args:
            db: Async database session
            build_id: Optional ID of the build
            created_by: Optional ID of the build owner
            profession_id: Optional ID of the profession
            elite_spec_id: Optional ID of the elite specialization
        """
        if not settings.CACHE_ENABLED:
            return

        # Invalidate specific build cache
        if build_id:
            await cache.delete(f"build:{build_id}")

        # Invalidate owner's builds cache
        if created_by:
            await cache.delete(f"builds:owner:{created_by}:*")

        # Invalidate profession-related caches
        if profession_id:
            await cache.delete(f"builds:profession:{profession_id}:*")

            # Also invalidate the profession cache as builds are often included
            profession = await db.get(Profession, profession_id)
            if profession:
                await cache.delete(f"profession:{profession_id}")

        # Invalidate elite spec-related caches
        if elite_spec_id:
            await cache.delete(f"builds:elite_spec:{elite_spec_id}:*")

            # Also invalidate the elite spec cache as builds are often included
            elite_spec = await db.get(EliteSpecialization, elite_spec_id)
            if elite_spec:
                await cache.delete(f"elite_spec:{elite_spec_id}")

                # Also invalidate the profession cache for this elite spec
                if elite_spec.profession_id:
                    await cache.delete(f"profession:{elite_spec.profession_id}")
                    await cache.delete(f"profession:{elite_spec.profession_id}:elite_specs")


# Create an instance of CRUDBuild to be imported and used in other modules
build = CRUDBuild(Build)
