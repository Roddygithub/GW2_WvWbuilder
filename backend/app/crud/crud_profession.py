"""
CRUD operations for Profession model with optimized loading and caching.
"""
from typing import Any, Dict, List, Optional, Union, Type, TypeVar

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.crud.base import CRUDBase
from app.models import (
    Profession, 
    EliteSpecialization,
    Build
)
from app.schemas.profession import ProfessionCreate, ProfessionUpdate
from app.core.cache import cache
from app.core.config import settings


class CRUDProfession(CRUDBase[Profession, ProfessionCreate, ProfessionUpdate]):
    """
    CRUD operations for Profession model with optimized loading and caching.
    """

    async def get(
        self, 
        db: AsyncSession, 
        id: Any,
        load_relations: bool = False
    ) -> Optional[Profession]:
        """
        Get a profession by ID with optional relation loading.
        
        Args:
            db: Async database session
            id: ID of the profession
            load_relations: If True, loads related models (elite specs, builds, etc.)
            
        Returns:
            Optional[Profession]: The profession if found, None otherwise
        """
        cache_key = f"profession:{id}"
        
        # Try to get from cache first
        if settings.CACHE_ENABLED and not load_relations:
            cached_profession = await cache.get(cache_key)
            if cached_profession is not None:
                return cached_profession
        
        # Build the base query
        query = select(Profession).where(Profession.id == id)
        
        # Load relations if requested
        if load_relations:
            query = query.options(
                selectinload(Profession.elite_specializations).selectinload(EliteSpecialization.builds),
                selectinload(Profession.builds)
            )
        
        # Execute query
        result = await db.execute(query)
        profession = result.scalars().first()
        
        # Cache the result if not loading relations
        if settings.CACHE_ENABLED and not load_relations and profession:
            await cache.set(cache_key, profession, ttl=settings.CACHE_TTL)
            
        return profession

    async def get_by_name(
        self, 
        db: AsyncSession, 
        *, 
        name: str,
        include_inactive: bool = False,
        load_relations: bool = False
    ) -> Optional[Profession]:
        """
        Get a profession by name with optional relation loading.
        
        Args:
            db: Async database session
            name: Name of the profession (case-insensitive)
            include_inactive: Whether to include inactive professions
            load_relations: If True, loads related models (elite specs, builds, etc.)
            
        Returns:
            Optional[Profession]: The profession if found, None otherwise
        """
        cache_key = f"profession:name:{name.lower()}"
        
        # Try to get from cache first
        if settings.CACHE_ENABLED and not load_relations and include_inactive:
            cached_profession = await cache.get(cache_key)
            if cached_profession is not None:
                return cached_profession
        
        # Build the base query
        query = select(Profession).where(func.lower(Profession.name) == name.lower())
        
        # Filter out inactive professions if needed
        if not include_inactive:
            query = query.where(Profession.is_active == True)  # noqa: E712
        
        # Load relations if requested
        if load_relations:
            query = query.options(
                selectinload(Profession.elite_specializations).selectinload(EliteSpecialization.builds),
                selectinload(Profession.builds)
            )
        
        # Execute query
        result = await db.execute(query)
        profession = result.scalars().first()
        
        # Cache the result if not loading relations and including inactive
        if settings.CACHE_ENABLED and not load_relations and include_inactive and profession:
            await cache.set(cache_key, profession, ttl=settings.CACHE_TTL)
            
        return profession

    async def get_multi(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        include_inactive: bool = False,
        load_relations: bool = False
    ) -> List[Profession]:
        """
        Get multiple professions with optional relation loading.
        
        Args:
            db: Async database session
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (for pagination)
            include_inactive: Whether to include inactive professions
            load_relations: If True, loads related models (elite specs, builds, etc.)
            
        Returns:
            List[Profession]: List of professions
        """
        cache_key = f"professions:all:{include_inactive}:{skip}:{limit}"
        
        # Try to get from cache first
        if settings.CACHE_ENABLED and not load_relations:
            cached_professions = await cache.get(cache_key)
            if cached_professions is not None:
                return cached_professions
        
        # Build the base query
        query = (
            select(Profession)
            .order_by(Profession.name.asc())
            .offset(skip)
            .limit(limit)
        )
        
        # Filter out inactive professions if needed
        if not include_inactive:
            query = query.where(Profession.is_active == True)  # noqa: E712
        
        # Load relations if requested
        if load_relations:
            query = query.options(
                selectinload(Profession.elite_specializations).selectinload(EliteSpecialization.builds),
                selectinload(Profession.builds)
            )
        
        # Execute query
        result = await db.execute(query)
        professions = result.scalars().all()
        
        # Cache the result if not loading relations
        if settings.CACHE_ENABLED and not load_relations:
            await cache.set(cache_key, professions, ttl=settings.CACHE_TTL)
            
        return professions

    async def get_with_elite_specs(
        self, 
        db: AsyncSession, 
        *, 
        id: int, 
        include_inactive: bool = False,
        load_builds: bool = False
    ) -> Optional[Profession]:
        """
        Get a profession with its elite specializations.
        
        Args:
            db: Async database session
            id: ID of the profession
            include_inactive: Whether to include inactive elite specializations
            load_builds: Whether to load builds for each elite specialization
            
        Returns:
            Optional[Profession]: The profession with elite specializations if found, None otherwise
        """
        cache_key = f"profession:{id}:elite_specs"
        
        # Try to get from cache first
        if settings.CACHE_ENABLED and not load_builds and include_inactive:
            cached_profession = await cache.get(cache_key)
            if cached_profession is not None:
                return cached_profession
        
        # Build the base query
        query = (
            select(Profession)
            .where(Profession.id == id)
            .options(selectinload(Profession.elite_specializations))
        )
        
        # Filter out inactive elite specs if needed
        if not include_inactive:
            query = query.options(
                selectinload(Profession.elite_specializations.and_(EliteSpecialization.is_active == True))  # noqa: E712
            )
        
        # Load builds if requested
        if load_builds:
            query = query.options(
                selectinload(Profession.elite_specializations).selectinload(EliteSpecialization.builds)
            )
        
        # Execute query
        result = await db.execute(query)
        profession = result.scalars().first()
        
        # Cache the result if not loading builds and including inactive
        if settings.CACHE_ENABLED and not load_builds and include_inactive and profession:
            await cache.set(cache_key, profession, ttl=settings.CACHE_TTL)
            
        return profession
        return result.scalars().first()


    async def create(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: ProfessionCreate
    ) -> Profession:
        """
        Create a new profession and invalidate related caches.
        
        Args:
            db: Async database session
            obj_in: Profession creation data
            
        Returns:
            Profession: The created profession
        """
        db_obj = Profession(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        # Invalidate related caches
        await self.invalidate_cache(db, db_obj.id, db_obj.name)
        
        return db_obj

    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: Profession, 
        obj_in: Union[ProfessionUpdate, Dict[str, Any]]
    ) -> Profession:
        """
        Update a profession and invalidate related caches.
        
        Args:
            db: Async database session
            db_obj: The profession to update
            obj_in: The update data
            
        Returns:
            Profession: The updated profession
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
            
        # Store old values for cache invalidation
        old_name = db_obj.name
            
        # Update the profession
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        # Invalidate caches for both old and new values if name changed
        if 'name' in update_data and update_data['name'] != old_name:
            await self.invalidate_cache(db, db_obj.id, old_name)
        else:
            await self.invalidate_cache(db, db_obj.id, db_obj.name)
        
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[Profession]:
        """
        Remove a profession and invalidate related caches.
        
        Args:
            db: Async database session
            id: ID of the profession to remove
            
        Returns:
            Optional[Profession]: The removed profession if it existed, None otherwise
        """
        profession = await self.get(db, id=id)
        if not profession:
            return None
            
        # Store values for cache invalidation
        profession_name = profession.name
            
        # Invalidate caches before deletion
        await self.invalidate_cache(db, id, profession_name)
            
        await db.delete(profession)
        await db.commit()
        return profession

    async def invalidate_cache(
        self, 
        db: AsyncSession, 
        profession_id: Optional[int] = None, 
        profession_name: Optional[str] = None
    ) -> None:
        """
        Invalidate cache for profession and related data.
        
        Args:
            db: Async database session
            profession_id: Optional ID of the profession
            profession_name: Optional name of the profession (for cache invalidation by name)
        """
        if not settings.CACHE_ENABLED:
            return
            
        # Invalidate specific profession caches
        if profession_id:
            await cache.delete(f"profession:{profession_id}")
            await cache.delete(f"profession:{profession_id}:elite_specs")
        
        if profession_name:
            await cache.delete(f"profession:name:{profession_name.lower()}")
        
        # Invalidate all professions list
        await cache.delete("professions:all:*")
        
        # Invalidate elite specs caches for this profession
        if profession_id:
            # Get all elite specs for this profession
            result = await db.execute(
                select(EliteSpecialization.id)
                .where(EliteSpecialization.profession_id == profession_id)
            )
            elite_spec_ids = result.scalars().all()
            
            # Invalidate cache for each elite spec
            for spec_id in elite_spec_ids:
                await cache.delete(f"elite_spec:{spec_id}")
                
            # Invalidate builds that use these elite specs
            for spec_id in elite_spec_ids:
                await cache.delete(f"builds:elite_spec:{spec_id}:*")


# Create an instance of CRUDProfession to be imported and used in other modules
profession = CRUDProfession(Profession)
