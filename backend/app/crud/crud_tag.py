"""
CRUD operations for Tag model with optimized loading and caching.
"""

from typing import Any, Dict, List, Optional, Union

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models import Tag, CompositionTag
from app.schemas.tag import TagCreate, TagUpdate
from app.core.cache import cache
from app.core.config import settings


class CRUDTag(CRUDBase[Tag, TagCreate, TagUpdate]):
    """
    CRUD operations for Tag model with optimized loading and caching.
    """

    async def get(self, db: AsyncSession, id: Any, load_relations: bool = False) -> Optional[Tag]:
        """
        Get a tag by ID with optional relation loading.

        Args:
            db: Async database session
            id: ID of the tag
            load_relations: If True, loads related models (compositions, etc.)

        Returns:
            Optional[Tag]: The tag if found, None otherwise
        """
        cache_key = f"tag:{id}"

        # Try to get from cache first
        if settings.CACHE_ENABLED and not load_relations:
            cached_tag = await cache.get(cache_key)
            if cached_tag is not None:
                return cached_tag

        # Build the base query
        query = select(Tag).where(Tag.id == id)

        # Load relations if requested
        if load_relations:
            query = query.options(selectinload(Tag.compositions).selectinload(CompositionTag.composition))

        # Execute query
        result = await db.execute(query)
        tag = result.scalars().first()

        # Cache the result if not loading relations
        if settings.CACHE_ENABLED and not load_relations and tag:
            await cache.set(cache_key, tag, ttl=settings.CACHE_TTL)

        return tag

    async def get_by_name(self, db: AsyncSession, *, name: str, load_relations: bool = False) -> Optional[Tag]:
        """
        Get a tag by name with optional relation loading.

        Args:
            db: Async database session
            name: Name of the tag (case-insensitive)
            load_relations: If True, loads related models (compositions, etc.)

        Returns:
            Optional[Tag]: The tag if found, None otherwise
        """
        cache_key = f"tag:name:{name.lower()}"

        # Try to get from cache first
        if settings.CACHE_ENABLED and not load_relations:
            cached_tag = await cache.get(cache_key)
            if cached_tag is not None:
                return cached_tag

        # Build the base query
        query = select(Tag).where(func.lower(Tag.name) == name.lower())

        # Load relations if requested
        if load_relations:
            query = query.options(selectinload(Tag.compositions).selectinload(CompositionTag.composition))

        # Execute query
        result = await db.execute(query)
        tag = result.scalars().first()

        # Cache the result if not loading relations
        if settings.CACHE_ENABLED and not load_relations and tag:
            await cache.set(cache_key, tag, ttl=settings.CACHE_TTL)

        return tag

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, load_relations: bool = False
    ) -> List[Tag]:
        """
        Get multiple tags with optional relation loading.

        Args:
            db: Async database session
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (for pagination)
            load_relations: If True, loads related models (compositions, etc.)

        Returns:
            List[Tag]: List of tags
        """
        cache_key = f"tags:all:{skip}:{limit}"

        # Try to get from cache first
        if settings.CACHE_ENABLED and not load_relations:
            cached_tags = await cache.get(cache_key)
            if cached_tags is not None:
                return cached_tags

        # Build the base query
        query = select(Tag).order_by(Tag.name.asc()).offset(skip).limit(limit)

        # Load relations if requested
        if load_relations:
            query = query.options(selectinload(Tag.compositions).selectinload(CompositionTag.composition))

        # Execute query
        result = await db.execute(query)
        tags = result.scalars().all()

        # Cache the result if not loading relations
        if settings.CACHE_ENABLED and not load_relations:
            await cache.set(cache_key, tags, ttl=settings.CACHE_TTL)

        return tags

    async def get_multi_by_composition(
        self, db: AsyncSession, *, composition_id: int, skip: int = 0, limit: int = 100, load_relations: bool = False
    ) -> List[Tag]:
        """
        Get multiple tags by composition ID with optional relation loading.

        Args:
            db: Async database session
            composition_id: ID of the composition
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (for pagination)
            load_relations: If True, loads related models (compositions, etc.)

        Returns:
            List[Tag]: List of tags for the specified composition
        """
        cache_key = f"composition:{composition_id}:tags:{skip}:{limit}"

        # Try to get from cache first
        if settings.CACHE_ENABLED and not load_relations:
            cached_tags = await cache.get(cache_key)
            if cached_tags is not None:
                return cached_tags

        # Build the base query with join to composition_tags
        query = (
            select(Tag)
            .join(CompositionTag, Tag.id == CompositionTag.tag_id)
            .where(CompositionTag.composition_id == composition_id)
            .order_by(Tag.name.asc())
            .offset(skip)
            .limit(limit)
        )

        # Load relations if requested
        if load_relations:
            query = query.options(selectinload(Tag.compositions).selectinload(CompositionTag.composition))

        # Execute query
        result = await db.execute(query)
        tags = result.scalars().all()

        # Cache the result if not loading relations
        if settings.CACHE_ENABLED and not load_relations:
            await cache.set(cache_key, tags, ttl=settings.CACHE_TTL)

        return tags

    async def create(self, db: AsyncSession, *, obj_in: TagCreate) -> Tag:
        """
        Create a new tag and invalidate related caches.

        Args:
            db: Async database session
            obj_in: Tag creation data

        Returns:
            Tag: The created tag
        """
        db_obj = Tag(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        # Invalidate related caches
        await self.invalidate_cache(db, db_obj.id, db_obj.name)

        return db_obj

    async def update(self, db: AsyncSession, *, db_obj: Tag, obj_in: Union[TagUpdate, Dict[str, Any]]) -> Tag:
        """
        Update a tag and invalidate related caches.

        Args:
            db: Async database session
            db_obj: The tag to update
            obj_in: The update data

        Returns:
            Tag: The updated tag
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        # Store old values for cache invalidation
        old_name = db_obj.name

        # Update the tag
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        # Invalidate caches for both old and new values if name changed
        if "name" in update_data and update_data["name"] != old_name:
            await self.invalidate_cache(db, db_obj.id, old_name)
        else:
            await self.invalidate_cache(db, db_obj.id, db_obj.name)

        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[Tag]:
        """
        Remove a tag and invalidate related caches.

        Args:
            db: Async database session
            id: ID of the tag to remove

        Returns:
            Optional[Tag]: The removed tag if it existed, None otherwise
        """
        tag = await self.get(db, id=id)
        if not tag:
            return None

        # Store values for cache invalidation
        tag_name = tag.name

        # Invalidate caches before deletion
        await self.invalidate_cache(db, id, tag_name)

        await db.delete(tag)
        await db.commit()
        return tag

    async def invalidate_cache(
        self, db: AsyncSession, tag_id: Optional[int] = None, tag_name: Optional[str] = None
    ) -> None:
        """
        Invalidate cache for tag and related data.

        Args:
            db: Async database session
            tag_id: Optional ID of the tag
            tag_name: Optional name of the tag (for cache invalidation by name)
        """
        if not settings.CACHE_ENABLED:
            return

        # Invalidate specific tag caches
        if tag_id:
            await cache.delete(f"tag:{tag_id}")

        if tag_name:
            await cache.delete(f"tag:name:{tag_name.lower()}")

        # Invalidate all tags list
        await cache.delete("tags:all:*")

        # Invalidate composition-tag relationship caches
        if tag_id:
            # Get all compositions that have this tag
            result = await db.execute(select(CompositionTag.composition_id).where(CompositionTag.tag_id == tag_id))
            composition_ids = result.scalars().all()

            # Invalidate cache for each composition's tags
            for comp_id in composition_ids:
                await cache.delete(f"composition:{comp_id}:tags:*")

            # Also invalidate the composition cache as tags are often included
            for comp_id in composition_ids:
                await cache.delete(f"composition:{comp_id}")


# Create an instance of CRUDTag to be imported and used in other modules
tag = CRUDTag(Tag)
