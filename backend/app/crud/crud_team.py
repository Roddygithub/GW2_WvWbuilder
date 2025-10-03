"""
CRUD operations for Team model.
"""
from typing import Any, Dict, List, Optional, Union, Type, TypeVar

from sqlalchemy import and_, or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.crud.base import CRUDBase
from app.models import (
    Team, 
    User, 
    TeamMember, 
    TeamRole, 
    Composition,
    CompositionTag,
    Tag
)
from app.schemas.team import TeamCreate, TeamUpdate, TeamMemberCreate, TeamMemberUpdate
from app.core.cache import cache
from app.core.config import settings


class CRUDTeam(CRUDBase[Team, TeamCreate, TeamUpdate]):
    """
    CRUD operations for Team model with optimized loading and caching.
    """

    async def get(
        self, 
        db: AsyncSession, 
        id: Any,
        load_relations: bool = False
    ) -> Optional[Team]:
        """
        Get a team by ID with optional relation loading.
        
        Args:
            db: Async database session
            id: ID of the team
            load_relations: If True, loads related models (members, compositions, etc.)
            
        Returns:
            Optional[Team]: The team if found, None otherwise
        """
        cache_key = f"team:{id}"
        
        # Try to get from cache first
        if settings.CACHE_ENABLED and not load_relations:
            cached_team = await cache.get(cache_key)
            if cached_team is not None:
                return cached_team
        
        # Build the base query
        query = select(Team).where(Team.id == id)
        
        # Load relations if requested
        if load_relations:
            query = query.options(
                selectinload(Team.members).joinedload(TeamMember.user),
                selectinload(Team.compositions).selectinload(Composition.tags).joinedload(CompositionTag.tag),
                selectinload(Team.owner)
            )
        
        # Execute query
        result = await db.execute(query)
        team = result.scalars().first()
        
        # Cache the result if not loading relations
        if settings.CACHE_ENABLED and not load_relations and team:
            await cache.set(cache_key, team, ttl=settings.CACHE_TTL)
            
        return team

    async def get_by_name(
        self, 
        db: AsyncSession, 
        *, 
        name: str,
        load_relations: bool = False
    ) -> Optional[Team]:
        """
        Get a team by name with optional relation loading.
        
        Args:
            db: Async database session
            name: Name of the team
            load_relations: If True, loads related models (members, compositions, etc.)
            
        Returns:
            Optional[Team]: The team if found, None otherwise
        """
        cache_key = f"team:name:{name}"
        
        # Try to get from cache first
        if settings.CACHE_ENABLED and not load_relations:
            cached_team = await cache.get(cache_key)
            if cached_team is not None:
                return cached_team
        
        # Build the base query
        query = select(Team).where(Team.name == name)
        
        # Load relations if requested
        if load_relations:
            query = query.options(
                selectinload(Team.members).joinedload(TeamMember.user),
                selectinload(Team.compositions).selectinload(Composition.tags).joinedload(CompositionTag.tag),
                selectinload(Team.owner)
            )
        
        # Execute query
        result = await db.execute(query)
        team = result.scalars().first()
        
        # Cache the result if not loading relations
        if settings.CACHE_ENABLED and not load_relations and team:
            await cache.set(cache_key, team, ttl=settings.CACHE_TTL)
            
        return team

    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: TeamCreate, owner_id: int
    ) -> Team:
        """
        Create a new team with an owner.
        
        Args:
            db: Async database session
            obj_in: Team creation data
            owner_id: ID of the owner
            
        Returns:
            Team: The created team
        """
        db_obj = Team(
            **obj_in.dict(exclude_unset=True),
            owner_id=owner_id,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        # Invalidate cache for owner's teams
        if settings.CACHE_ENABLED:
            await cache.delete(f"teams:owner:{owner_id}:*")
            
        return db_obj

    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: Team, 
        obj_in: Union[TeamUpdate, Dict[str, Any]]
    ) -> Team:
        """
        Update a team and invalidate related caches.
        
        Args:
            db: Async database session
            db_obj: The team to update
            obj_in: The update data
            
        Returns:
            Team: The updated team
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # Update the team
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        # Invalidate caches
        await self.invalidate_cache(db, db_obj.id)
        
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[Team]:
        """
        Remove a team and invalidate related caches.
        
        Args:
            db: Async database session
            id: ID of the team to remove
            
        Returns:
            Optional[Team]: The removed team if it existed, None otherwise
        """
        team = await self.get(db, id=id)
        if not team:
            return None
            
        # Invalidate caches before deletion
        await self.invalidate_cache(db, id)
            
        await db.delete(team)
        await db.commit()
        return team

    async def add_member(
        self, 
        db: AsyncSession, 
        *, 
        team_id: int, 
        user_id: int, 
        role: str = "member"
    ) -> bool:
        """Add a member to a team."""
        # Check if user is already a member
        stmt = select(team_members).where(
            (team_members.c.team_id == team_id) & 
            (team_members.c.user_id == user_id)
        )
        result = await db.execute(stmt)
        if result.first():
            return False  # User is already a member

        # Add user to team
        stmt = team_members.insert().values(
            team_id=team_id,
            user_id=user_id,
            role=role
        )
        await db.execute(stmt)
        await db.commit()
        return True

    async def remove_member(
        self, db: AsyncSession, *, team_id: int, user_id: int
    ) -> bool:
        """Remove a member from a team."""
        # Check if user is a member
        stmt = select(team_members).where(
            (team_members.c.team_id == team_id) & 
            (team_members.c.user_id == user_id)
        )
        result = await db.execute(stmt)
        if not result.first():
            return False  # User is not a member

        # Remove user from team
        stmt = team_members.delete().where(
            (team_members.c.team_id == team_id) & 
            (team_members.c.user_id == user_id)
        )
        await db.execute(stmt)
        await db.commit()
        return True

    async def get_members(
        self, 
        db: AsyncSession, 
        *, 
        team_id: int, 
        skip: int = 0, 
        limit: int = 100,
        load_teams: bool = False
    ) -> List[User]:
        """
        Get all members of a team with optional team loading.
        
        Args:
            db: Async database session
            team_id: ID of the team
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (for pagination)
            load_teams: If True, loads the teams for each member
            
        Returns:
            List[User]: List of team members
        """
        cache_key = f"team:{team_id}:members:{skip}:{limit}"
        
        # Try to get from cache first
        if settings.CACHE_ENABLED:
            cached_members = await cache.get(cache_key)
            if cached_members is not None:
                return cached_members
        
        # Build the base query
        query = (
            select(User)
            .join(team_members, User.id == team_members.c.user_id)
            .where(team_members.c.team_id == team_id)
            .offset(skip)
            .limit(limit)
        )
        
        # Load teams if requested
        if load_teams:
            query = query.options(selectinload(User.teams))
        
        # Execute query
        result = await db.execute(query)
        members = result.scalars().all()
        
        # Cache the result
        if settings.CACHE_ENABLED:
            await cache.set(cache_key, members, ttl=settings.CACHE_TTL)
            
        return members

    async def is_member(
        self, db: AsyncSession, *, team_id: int, user_id: int
    ) -> bool:
        """Check if a user is a member of a team."""
        result = await db.execute(
            select(team_members)
            .where(
                (team_members.c.team_id == team_id) & 
                (team_members.c.user_id == user_id)
            )
        )
        return result.first() is not None

    async def is_owner(
        self, db: AsyncSession, *, team_id: int, user_id: int
    ) -> bool:
        """Check if a user is the owner of a team."""
        result = await db.execute(
            select(Team)
            .where(
                (Team.id == team_id) & 
                (Team.owner_id == user_id)
            )
        )
        return result.first() is not None

    async def get_user_teams(
        self, 
        db: AsyncSession, 
        *, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        load_relations: bool = False
    ) -> List[Team]:
        """
        Get all teams a user is a member of with optional relation loading.
        
        Args:
            db: Async database session
            user_id: ID of the user
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (for pagination)
            load_relations: If True, loads related models (members, builds, compositions)
            
        Returns:
            List[Team]: List of teams the user is a member of
        """
        cache_key = f"user:{user_id}:teams:{skip}:{limit}"
        
        # Try to get from cache first
        if settings.CACHE_ENABLED:
            cached_teams = await cache.get(cache_key)
            if cached_teams is not None:
                return cached_teams
        
        # Build the base query
        query = (
            select(Team)
            .join(team_members, Team.id == team_members.c.team_id)
            .where(team_members.c.user_id == user_id)
            .order_by(Team.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        # Load relations if requested
        if load_relations:
            query = query.options(
                selectinload(Team.member_associations).joinedload(TeamMember.user),
                selectinload(Team.builds),
                selectinload(Team.compositions)
            )
        
        # Execute query
        result = await db.execute(query)
        teams = result.scalars().all()
        
        # Cache the result
        if settings.CACHE_ENABLED:
            await cache.set(cache_key, teams, ttl=settings.CACHE_TTL)
            
        return teams


    async def invalidate_cache(self, team_id: int) -> None:
        """Invalidate cache for a team and its related data."""
        if not settings.CACHE_ENABLED:
            return
            
        # Invalidate team cache
        await cache.delete(f"team:name:{team_id}")
        
        # Invalidate team members cache
        await cache.delete(f"team:{team_id}:members:*")
        
        # Invalidate user teams cache for all members
        members = await self.get_members(db, team_id=team_id)
        for member in members:
            await cache.delete(f"user:{member.id}:teams:*")
        
        # Invalidate team lists cache
        await cache.delete("teams:owner:*")
        await cache.delete("teams:public")


    async def invalidate_cache(self, db: AsyncSession, team_id: int) -> None:
        """
        Invalidate cache for a team and related data.
        
        Args:
            db: Async database session
            team_id: ID of the team
        """
        if not settings.CACHE_ENABLED:
            return
            
        # Invalidate team cache
        await cache.delete(f"team:{team_id}")
        await cache.delete(f"team:name:*")
        
        # Invalidate team lists cache
        await cache.delete("teams:public:*")
        await cache.delete("teams:owner:*")
        
        # Invalidate related caches
        team = await self.get(db, team_id)
        if team:
            # Invalidate owner's teams cache
            await cache.delete(f"teams:owner:{team.owner_id}:*")
            
            # Invalidate team members cache
            await cache.delete(f"team:{team_id}:members")
            
            # Invalidate team compositions cache
            await cache.delete(f"team:{team_id}:compositions")


# Create an instance of CRUDTeam to be imported and used in other modules
team = CRUDTeam(Team)
