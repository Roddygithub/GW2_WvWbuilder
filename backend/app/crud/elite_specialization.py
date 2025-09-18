from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from app.crud.base import CRUDBase
from app.models import EliteSpecialization as EliteSpecModel
from app.schemas.profession import EliteSpecializationCreate, EliteSpecializationUpdate


class CRUDEliteSpecialization(CRUDBase[EliteSpecModel, EliteSpecializationCreate, EliteSpecializationUpdate]):
    """CRUD operations for EliteSpecialization model with both sync and async support."""

    def get_by_name_and_profession(
        self, db: Session, *, name: str, profession_id: int
    ) -> Optional[EliteSpecModel]:
        """Get an elite specialization by name and profession ID (synchronous)."""
        stmt = select(self.model).where(
            and_(
                self.model.name == name,
                self.model.profession_id == profession_id
            )
        )
        return db.scalars(stmt).first()

    async def get_by_name_and_profession_async(
        self, db: AsyncSession, *, name: str, profession_id: int
    ) -> Optional[EliteSpecModel]:
        """Get an elite specialization by name and profession ID (asynchronous)."""
        stmt = select(self.model).where(
            and_(
                self.model.name == name,
                self.model.profession_id == profession_id
            )
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    def get_by_profession(
        self, db: Session, *, profession_id: int, skip: int = 0, limit: int = 100
    ) -> List[EliteSpecModel]:
        """Get all elite specializations for a profession (synchronous)."""
        stmt = (
            select(self.model)
            .where(self.model.profession_id == profession_id)
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

    async def get_by_profession_async(
        self, db: AsyncSession, *, profession_id: int, skip: int = 0, limit: int = 100
    ) -> List[EliteSpecModel]:
        """Get all elite specializations for a profession (asynchronous)."""
        stmt = (
            select(self.model)
            .where(self.model.profession_id == profession_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    def get_by_specialization_id(
        self, db: Session, *, spec_id: int
    ) -> Optional[EliteSpecModel]:
        """Get an elite specialization by its specialization ID (synchronous)."""
        stmt = select(self.model).where(self.model.specialization_id == spec_id)
        return db.scalars(stmt).first()

    async def get_by_specialization_id_async(
        self, db: AsyncSession, *, spec_id: int
    ) -> Optional[EliteSpecModel]:
        """Get an elite specialization by its specialization ID (asynchronous)."""
        stmt = select(self.model).where(self.model.specialization_id == spec_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    def get_with_profession(
        self, db: Session, *, id: int
    ) -> Optional[EliteSpecModel]:
        """Get an elite specialization with its profession (synchronous)."""
        stmt = (
            select(self.model)
            .where(self.model.id == id)
            .options(selectinload(self.model.profession))
        )
        return db.scalars(stmt).first()

    async def get_with_profession_async(
        self, db: AsyncSession, *, id: int
    ) -> Optional[EliteSpecModel]:
        """Get an elite specialization with its profession (asynchronous)."""
        stmt = (
            select(self.model)
            .where(self.model.id == id)
            .options(selectinload(self.model.profession))
        )
        result = await db.execute(stmt)
        return result.unique().scalars().first()

    def get_all_names(self, db: Session) -> List[str]:
        """Get all elite specialization names (synchronous)."""
        stmt = select(self.model.name)
        return list(db.scalars(stmt).all())

    async def get_all_names_async(self, db: AsyncSession) -> List[str]:
        """Get all elite specialization names (asynchronous)."""
        stmt = select(self.model.name)
        result = await db.execute(stmt)
        return [row[0] for row in result.all()]

    def get_id_by_name(self, db: Session, *, name: str) -> Optional[int]:
        """Get elite specialization ID by name (synchronous)."""
        stmt = select(self.model.id).where(self.model.name == name)
        return db.scalars(stmt).first()

    async def get_id_by_name_async(self, db: AsyncSession, *, name: str) -> Optional[int]:
        """Get elite specialization ID by name (asynchronous)."""
        stmt = select(self.model.id).where(self.model.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


# Create a singleton instance
elite_specialization = CRUDEliteSpecialization(EliteSpecModel)
