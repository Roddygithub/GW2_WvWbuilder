from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from app.crud.base import CRUDBase
from app.models import Role as RoleModel
from app.schemas.role import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[RoleModel, RoleCreate, RoleUpdate]):
    """CRUD operations for Role model with both sync and async support."""

    def get_by_name(self, db: Session, *, name: str) -> Optional[RoleModel]:
        """Get a role by name (synchronous)."""
        stmt = select(self.model).where(self.model.name == name)
        return db.scalars(stmt).first()

    async def get_by_name_async(self, db: AsyncSession, *, name: str) -> Optional[RoleModel]:
        """Get a role by name (asynchronous)."""
        stmt = select(self.model).where(self.model.name == name)
        result = await db.execute(stmt)
        return result.scalars().first()

    def get_by_permission_level(
        self, db: Session, *, permission_level: int
    ) -> List[RoleModel]:
        """Get all roles with a specific permission level (synchronous)."""
        stmt = select(self.model).where(self.model.permission_level == permission_level)
        return list(db.scalars(stmt).all())

    async def get_by_permission_level_async(
        self, db: AsyncSession, *, permission_level: int
    ) -> List[RoleModel]:
        """Get all roles with a specific permission level (asynchronous)."""
        stmt = select(self.model).where(self.model.permission_level == permission_level)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    def get_multi_by_permission_range(
        self, db: Session, *, min_level: int = 0, max_level: int = 100, skip: int = 0, limit: int = 100
    ) -> List[RoleModel]:
        """Get roles within a permission level range (synchronous)."""
        stmt = (
            select(self.model)
            .where(
                and_(
                    self.model.permission_level >= min_level,
                    self.model.permission_level <= max_level
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

    async def get_multi_by_permission_range_async(
        self, db: AsyncSession, *, min_level: int = 0, max_level: int = 100, skip: int = 0, limit: int = 100
    ) -> List[RoleModel]:
        """Get roles within a permission level range (asynchronous)."""
        stmt = (
            select(self.model)
            .where(
                and_(
                    self.model.permission_level >= min_level,
                    self.model.permission_level <= max_level
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    def get_with_users(self, db: Session, *, id: int) -> Optional[RoleModel]:
        """Get a role with its users (synchronous)."""
        stmt = (
            select(self.model)
            .where(self.model.id == id)
            .options(selectinload(self.model.users))
        )
        return db.scalars(stmt).first()

    async def get_with_users_async(self, db: AsyncSession, *, id: int) -> Optional[RoleModel]:
        """Get a role with its users (asynchronous)."""
        stmt = (
            select(self.model)
            .where(self.model.id == id)
            .options(selectinload(self.model.users))
        )
        result = await db.execute(stmt)
        return result.unique().scalars().first()

    def get_all_names(self, db: Session) -> List[str]:
        """Get all role names (synchronous)."""
        stmt = select(self.model.name)
        return list(db.scalars(stmt).all())

    async def get_all_names_async(self, db: AsyncSession) -> List[str]:
        """Get all role names (asynchronous)."""
        stmt = select(self.model.name)
        result = await db.execute(stmt)
        return [row[0] for row in result.all()]

    def get_id_by_name(self, db: Session, *, name: str) -> Optional[int]:
        """Get role ID by name (synchronous)."""
        stmt = select(self.model.id).where(self.model.name == name)
        return db.scalars(stmt).first()

    async def get_id_by_name_async(self, db: AsyncSession, *, name: str) -> Optional[int]:
        """Get role ID by name (asynchronous)."""
        stmt = select(self.model.id).where(self.model.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    def get_default_role(self, db: Session) -> Optional[RoleModel]:
        """Get the default role (synchronous)."""
        stmt = select(self.model).where(self.model.is_default == True)  # noqa: E712
        return db.scalars(stmt).first()

    async def get_default_role_async(self, db: AsyncSession) -> Optional[RoleModel]:
        """Get the default role (asynchronous)."""
        stmt = select(self.model).where(self.model.is_default == True)  # noqa: E712
        result = await db.execute(stmt)
        return result.scalars().first()


# Create a singleton instance
role = CRUDRole(RoleModel)
