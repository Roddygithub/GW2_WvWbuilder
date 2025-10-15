from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

# Type aliases for better type hints
ModelDict = Dict[str, Any]
ModelOrDict = Union[ModelType, ModelDict]


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base class for CRUD operations with both sync and async support.

    This class provides common database operations that can be used with both
    synchronous and asynchronous SQLAlchemy sessions.
    """

    def __init__(self, model: Type[ModelType]):
        """Initialize CRUD class with the given model.

        Args:
            model: SQLAlchemy model class
        """
        self.model = model
        self._select_stmt: Select = select(self.model)

    # --- Synchronous methods ---

    def get(self, db: Session, id: Any, **kwargs) -> Optional[ModelType]:
        """Get a single object by ID.

        Args:
            db: Database session
            id: ID of the object to retrieve
            **kwargs: Additional query options (e.g., options for eager loading)

        Returns:
            The object if found, None otherwise
        """
        stmt = self._select_stmt.where(self.model.id == id)
        if "options" in kwargs:
            stmt = stmt.options(*kwargs["options"])
        return db.scalars(stmt).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, **filters
    ) -> List[ModelType]:
        """Get multiple objects with optional filtering and pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            **filters: Key-value pairs to filter by (column=value)

        Returns:
            List of objects matching the criteria
        """
        stmt = self._select_stmt.offset(skip).limit(limit)

        # Apply filters
        for key, value in filters.items():
            if hasattr(self.model, key):
                stmt = stmt.where(getattr(self.model, key) == value)

        return list(db.scalars(stmt).all())

    def create(
        self, db: Session, *, obj_in: Union[CreateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Create a new object.

        Args:
            db: Database session
            obj_in: Object data as Pydantic model or dictionary

        Returns:
            The created object
        """
        if isinstance(obj_in, BaseModel):
            obj_data = obj_in.model_dump(exclude_unset=True)
        else:
            obj_data = obj_in

        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        commit: bool = True,
    ) -> ModelType:
        """Update an existing object.

        Args:
            db: Database session
            db_obj: Object to update
            obj_in: Updated data as Pydantic model or dictionary
            commit: Whether to commit the transaction

        Returns:
            The updated object
        """
        if isinstance(obj_in, BaseModel):
            update_data = obj_in.model_dump(exclude_unset=True)
        else:
            update_data = obj_in

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        if commit:
            db.commit()
            db.refresh(db_obj)

        return db_obj

    def remove(self, db: Session, *, id: Any) -> Optional[ModelType]:
        """Remove an object by ID.

        Args:
            db: Database session
            id: ID of the object to remove

        Returns:
            The removed object if found, None otherwise
        """
        obj = self.get(db, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    # --- Asynchronous methods ---

    async def get_async(
        self, db: AsyncSession, id: Any, **kwargs
    ) -> Optional[ModelType]:
        """Asynchronously get a single object by ID.

        Args:
            db: Async database session
            id: ID of the object to retrieve
            **kwargs: Additional query options (e.g., options for eager loading)

        Returns:
            The object if found, None otherwise
        """
        stmt = self._select_stmt.where(self.model.id == id)
        if "options" in kwargs:
            stmt = stmt.options(*kwargs["options"])
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_multi_async(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, **filters
    ) -> List[ModelType]:
        """Asynchronously get multiple objects with optional filtering and pagination.

        Args:
            db: Async database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            **filters: Key-value pairs to filter by (column=value)

        Returns:
            List of objects matching the criteria
        """
        stmt = self._select_stmt.offset(skip).limit(limit)

        # Apply filters
        for key, value in filters.items():
            if hasattr(self.model, key):
                stmt = stmt.where(getattr(self.model, key) == value)

        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create_async(
        self, db: AsyncSession, *, obj_in: Union[CreateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Asynchronously create a new object.

        Args:
            db: Async database session
            obj_in: Object data as Pydantic model or dictionary

        Returns:
            The created object
        """
        if isinstance(obj_in, BaseModel):
            obj_data = obj_in.model_dump(exclude_unset=True)
        else:
            obj_data = obj_in

        db_obj = self.model(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_async(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        commit: bool = True,
    ) -> ModelType:
        """Asynchronously update an existing object.

        Args:
            db: Async database session
            db_obj: Object to update
            obj_in: Updated data as Pydantic model or dictionary
            commit: Whether to commit the transaction

        Returns:
            The updated object
        """
        if isinstance(obj_in, BaseModel):
            update_data = obj_in.model_dump(exclude_unset=True)
        else:
            update_data = obj_in

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        if commit:
            await db.commit()
            await db.refresh(db_obj)

        return db_obj

    async def remove_async(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        """Asynchronously remove an object by ID.

        Args:
            db: Async database session
            id: ID of the object to remove

        Returns:
            The removed object if found, None otherwise
        """
        obj = await self.get_async(db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj
