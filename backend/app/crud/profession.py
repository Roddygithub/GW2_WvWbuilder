from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models import Profession as ProfessionModel
from app.schemas.profession import ProfessionCreate, ProfessionUpdate


class CRUDProfession(CRUDBase[ProfessionModel, ProfessionCreate, ProfessionUpdate]):
    """CRUD operations for Profession model with both sync and async support."""

    def get_by_name(self, db: Session, *, name: str) -> Optional[ProfessionModel]:
        """Get a profession by name (synchronous)."""
        stmt = select(self.model).where(self.model.name == name)
        return db.scalars(stmt).first()

    async def get_by_name_async(
        self, db: AsyncSession, *, name: str
    ) -> Optional[ProfessionModel]:
        """Get a profession by name (asynchronous)."""
        stmt = select(self.model).where(self.model.name == name)
        result = await db.execute(stmt)
        return result.scalars().first()

    def get_with_elite_specs(
        self, db: Session, *, id: int
    ) -> Optional[ProfessionModel]:
        """Get a profession with its elite specializations (synchronous)."""
        stmt = (
            select(self.model)
            .where(self.model.id == id)
            .options(selectinload(self.model.elite_specializations))
        )
        return db.scalars(stmt).first()

    async def get_with_elite_specs_async(
        self, db: AsyncSession, *, id: int
    ) -> Optional[ProfessionModel]:
        """Get a profession with its elite specializations (asynchronous)."""
        stmt = (
            select(self.model)
            .where(self.model.id == id)
            .options(selectinload(self.model.elite_specializations))
        )
        result = await db.execute(stmt)
        return result.unique().scalars().first()

    def get_multi_by_game_mode(
        self, db: Session, *, game_mode: str, skip: int = 0, limit: int = 100
    ) -> List[ProfessionModel]:
        """Get multiple professions by game mode (synchronous)."""
        stmt = (
            select(self.model)
            .where(self.model.game_modes.contains([game_mode]))
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

    async def get_multi_by_game_mode_async(
        self, db: AsyncSession, *, game_mode: str, skip: int = 0, limit: int = 100
    ) -> List[ProfessionModel]:
        """Get multiple professions by game mode (asynchronous)."""
        stmt = (
            select(self.model)
            .where(self.model.game_modes.contains([game_mode]))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    def get_all_names(self, db: Session) -> List[str]:
        """Get all profession names (synchronous)."""
        stmt = select(self.model.name)
        return list(db.scalars(stmt).all())

    async def get_all_names_async(self, db: AsyncSession) -> List[str]:
        """Get all profession names (asynchronous)."""
        stmt = select(self.model.name)
        result = await db.execute(stmt)
        return [row[0] for row in result.all()]

    def get_id_by_name(self, db: Session, *, name: str) -> Optional[int]:
        """Get profession ID by name (synchronous)."""
        stmt = select(self.model.id).where(self.model.name == name)
        return db.scalars(stmt).first()

    async def get_id_by_name_async(
        self, db: AsyncSession, *, name: str
    ) -> Optional[int]:
        """Get profession ID by name (asynchronous)."""
        stmt = select(self.model.id).where(self.model.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


# Create a singleton instance
profession = CRUDProfession(ProfessionModel)
