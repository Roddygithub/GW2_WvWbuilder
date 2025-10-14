"""
CRUD operations for TeamMember model with optimized loading and caching.
"""

from typing import Any, Dict, List, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models import TeamMember, User, Team
from app.schemas.team_member import TeamMemberCreate, TeamMemberUpdate
from app.core.cache import cache
from app.core.config import settings


class CRUDTeamMember(CRUDBase[TeamMember, TeamMemberCreate, TeamMemberUpdate]):
    """
    CRUD operations for TeamMember model with optimized loading and caching.
    """

    async def get(self, db: AsyncSession, id: Any, load_relations: bool = False) -> Optional[TeamMember]:
        """
        Get a team member by ID with optional relation loading.

        Args:
            db: Async database session
            id: ID of the team member
            load_relations: If True, loads related models (user, team, etc.)

        Returns:
            Optional[TeamMember]: The team member if found, None otherwise
        """
        cache_key = f"team_member:{id}"

        # Try to get from cache first
        if settings.CACHE_ENABLED and not load_relations:
            cached_member = await cache.get(cache_key)
            if cached_member is not None:
                return cached_member

        # Build the base query
        query = select(TeamMember).where(TeamMember.id == id)

        # Load relations if requested
        if load_relations:
            query = query.options(
                selectinload(TeamMember.user),
                selectinload(TeamMember.team).selectinload(Team.members).joinedload(TeamMember.user),
                selectinload(TeamMember.role),
            )

        # Execute query
        result = await db.execute(query)
        member = result.scalars().first()

        # Cache the result if not loading relations
        if settings.CACHE_ENABLED and not load_relations and member:
            await cache.set(cache_key, member, ttl=settings.CACHE_TTL)

        return member

    async def get_by_team_and_user(
        self, db: AsyncSession, *, team_id: int, user_id: int, load_relations: bool = False
    ) -> Optional[TeamMember]:
        """
        Get a team member by team ID and user ID with optional relation loading.

        Args:
            db: Async database session
            team_id: ID of the team
            user_id: ID of the user
            load_relations: If True, loads related models (user, team, etc.)

        Returns:
            Optional[TeamMember]: The team member if found, None otherwise
        """
        cache_key = f"team:{team_id}:user:{user_id}"

        # Try to get from cache first
        if settings.CACHE_ENABLED and not load_relations:
            cached_member = await cache.get(cache_key)
            if cached_member is not None:
                return cached_member

        # Build the base query
        query = select(TeamMember).where((TeamMember.team_id == team_id) & (TeamMember.user_id == user_id))

        # Load relations if requested
        if load_relations:
            query = query.options(
                selectinload(TeamMember.user),
                selectinload(TeamMember.team).selectinload(Team.members).joinedload(TeamMember.user),
                selectinload(TeamMember.role),
            )

        # Execute query
        result = await db.execute(query)
        member = result.scalars().first()

        # Cache the result if not loading relations
        if settings.CACHE_ENABLED and not load_relations and member:
            await cache.set(cache_key, member, ttl=settings.CACHE_TTL)

        return member

    async def get_multi_by_team(
        self, db: AsyncSession, *, team_id: int, skip: int = 0, limit: int = 100, load_relations: bool = False
    ) -> List[TeamMember]:
        """
        Get multiple team members by team ID with optional relation loading.

        Args:
            db: Async database session
            team_id: ID of the team
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (for pagination)
            load_relations: If True, loads related models (user, role, etc.)

        Returns:
            List[TeamMember]: List of team members for the specified team
        """
        cache_key = f"team:{team_id}:members:{skip}:{limit}"

        # Try to get from cache first
        if settings.CACHE_ENABLED and not load_relations:
            cached_members = await cache.get(cache_key)
            if cached_members is not None:
                return cached_members

        # Build the base query
        query = (
            select(TeamMember)
            .where(TeamMember.team_id == team_id)
            .order_by(TeamMember.joined_at.desc())
            .offset(skip)
            .limit(limit)
        )

        # Load relations if requested
        if load_relations:
            query = query.options(selectinload(TeamMember.user), selectinload(TeamMember.role))

        # Execute query
        result = await db.execute(query)
        members = result.scalars().all()

        # Cache the result if not loading relations
        if settings.CACHE_ENABLED and not load_relations:
            await cache.set(cache_key, members, ttl=settings.CACHE_TTL)

        return members

    async def get_multi_by_user(
        self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100, load_relations: bool = False
    ) -> List[TeamMember]:
        """
        Get multiple team members by user ID with optional relation loading.

        Args:
            db: Async database session
            user_id: ID of the user
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (for pagination)
            load_relations: If True, loads related models (team, role, etc.)

        Returns:
            List[TeamMember]: List of team members for the specified user
        """
        cache_key = f"user:{user_id}:teams:{skip}:{limit}"

        # Try to get from cache first
        if settings.CACHE_ENABLED and not load_relations:
            cached_memberships = await cache.get(cache_key)
            if cached_memberships is not None:
                return cached_memberships

        # Build the base query
        query = (
            select(TeamMember)
            .where(TeamMember.user_id == user_id)
            .order_by(TeamMember.joined_at.desc())
            .offset(skip)
            .limit(limit)
        )

        # Load relations if requested
        if load_relations:
            query = query.options(selectinload(TeamMember.team).selectinload(Team.owner), selectinload(TeamMember.role))

        # Execute query
        result = await db.execute(query)
        memberships = result.scalars().all()

        # Cache the result if not loading relations
        if settings.CACHE_ENABLED and not load_relations:
            await cache.set(cache_key, memberships, ttl=settings.CACHE_TTL)

        return memberships

    async def create(self, db: AsyncSession, *, obj_in: TeamMemberCreate) -> TeamMember:
        """
        Create a new team member and invalidate related caches.

        Args:
            db: Async database session
            obj_in: Team member creation data

        Returns:
            TeamMember: The created team member
        """
        db_obj = TeamMember(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        # Invalidate related caches
        await self.invalidate_cache(db, db_obj.id, db_obj.team_id, db_obj.user_id)

        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: TeamMember, obj_in: Union[TeamMemberUpdate, Dict[str, Any]]
    ) -> TeamMember:
        """
        Update a team member and invalidate related caches.

        Args:
            db: Async database session
            db_obj: The team member to update
            obj_in: The update data

        Returns:
            TeamMember: The updated team member
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        # Store old values for cache invalidation
        old_team_id = db_obj.team_id
        old_user_id = db_obj.user_id

        # Update the team member
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        # Invalidate caches for both old and new values if they changed
        team_id = db_obj.team_id
        user_id = db_obj.user_id

        if team_id != old_team_id or user_id != old_user_id:
            # Invalidate caches for old values
            await self.invalidate_cache(db, db_obj.id, old_team_id, old_user_id)

        # Invalidate caches for new values
        await self.invalidate_cache(db, db_obj.id, team_id, user_id)

        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[TeamMember]:
        """
        Remove a team member and invalidate related caches.

        Args:
            db: Async database session
            id: ID of the team member to remove

        Returns:
            Optional[TeamMember]: The removed team member if it existed, None otherwise
        """
        team_member = await self.get(db, id=id)
        if not team_member:
            return None

        # Store values for cache invalidation
        team_id = team_member.team_id
        user_id = team_member.user_id

        # Invalidate caches before deletion
        await self.invalidate_cache(db, id, team_id, user_id)

        await db.delete(team_member)
        await db.commit()
        return team_member

    async def invalidate_cache(
        self,
        db: AsyncSession,
        member_id: Optional[int] = None,
        team_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> None:
        """
        Invalidate cache for team member and related data.

        Args:
            db: Async database session
            member_id: Optional ID of the team member
            team_id: Optional ID of the team
            user_id: Optional ID of the user
        """
        if not settings.CACHE_ENABLED:
            return

        # Invalidate specific member cache
        if member_id:
            await cache.delete(f"team_member:{member_id}")

        # Invalidate team-related caches
        if team_id:
            await cache.delete(f"team:{team_id}:members")
            await cache.delete(f"team:{team_id}:members:*")

            # Also invalidate team cache as member lists are often included
            team = await db.get(Team, team_id)
            if team:
                await cache.delete(f"team:{team_id}")

        # Invalidate user-related caches
        if user_id:
            await cache.delete(f"user:{user_id}:teams")
            await cache.delete(f"user:{user_id}:teams:*")

            # Also invalidate user cache if it includes team info
            user = await db.get(User, user_id)
            if user:
                await cache.delete(f"user:{user_id}")


# Create an instance of CRUDTeamMember to be imported and used in other modules
team_member = CRUDTeamMember(TeamMember)
