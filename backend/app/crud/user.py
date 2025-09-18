from __future__ import annotations

from typing import Any, Dict, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from app.core import security
from app.crud.base import CRUDBase
from app.models import User as UserModel
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[UserModel, UserCreate, UserUpdate]):
    """CRUD operations for User model with both sync and async support."""

    def get_by_email(self, db: Session, *, email: str) -> Optional[UserModel]:
        """Get a user by email (synchronous)."""
        stmt = select(self.model).where(self.model.email == email)
        return db.scalars(stmt).first()

    async def get_by_email_async(self, db: AsyncSession, *, email: str) -> Optional[UserModel]:
        """Get a user by email (asynchronous)."""
        stmt = select(self.model).where(self.model.email == email)
        result = await db.execute(stmt)
        return result.scalars().first()

    def get_with_roles(self, db: Session, *, id: int) -> Optional[UserModel]:
        """Get a user with roles loaded (synchronous)."""
        stmt = select(self.model).where(self.model.id == id).options(selectinload(self.model.roles))
        return db.scalars(stmt).first()

    async def get_with_roles_async(self, db: AsyncSession, *, id: int) -> Optional[UserModel]:
        """Get a user with roles loaded (asynchronous)."""
        stmt = select(self.model).where(self.model.id == id).options(selectinload(self.model.roles))
        result = await db.execute(stmt)
        return result.scalars().first()

    def is_superuser(self, user: UserModel) -> bool:
        """Check if user is a superuser."""
        return bool(getattr(user, "is_superuser", False))

    def create(self, db: Session, *, obj_in: Union[UserCreate, Dict[str, Any]]) -> UserModel:
        """Create a new user (synchronous)."""
        if isinstance(obj_in, dict):
            user_data = obj_in.copy()
        else:
            user_data = obj_in.model_dump(exclude_unset=True)

        # Check if email already exists
        if "email" in user_data and self.get_by_email(db, email=user_data["email"]):
            raise ValueError("Email already registered")

        # Handle password hashing
        if "password" in user_data:
            hashed_password = security.get_password_hash(user_data["password"])
            user_data["hashed_password"] = hashed_password
            del user_data["password"]

        return super().create(db, obj_in=user_data)

    async def create_async(
        self, db: AsyncSession, *, obj_in: Union[UserCreate, Dict[str, Any]]
    ) -> UserModel:
        """Create a new user (asynchronous)."""
        if isinstance(obj_in, dict):
            user_data = obj_in.copy()
        else:
            user_data = obj_in.model_dump(exclude_unset=True)

        # Check if email already exists
        if "email" in user_data and await self.get_by_email_async(db, email=user_data["email"]):
            raise ValueError("Email already registered")

        # Handle password hashing
        if "password" in user_data:
            hashed_password = security.get_password_hash(user_data["password"])
            user_data["hashed_password"] = hashed_password
            del user_data["password"]

        return await super().create_async(db, obj_in=user_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[UserModel]:
        """Authenticate a user (synchronous)."""
        user = self.get_by_email(db, email=email)
        if not user or not user.is_active:
            return None
        
        # For testing or when password is stored in plain text
        if user.hashed_password == password:
            return user
            
        # Verify hashed password
        if not security.verify_password(password, user.hashed_password):
            return None
            
        return user

    async def authenticate_async(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[UserModel]:
        """Authenticate a user (asynchronous)."""
        user = await self.get_by_email_async(db, email=email)
        if not user or not user.is_active:
            return None
            
        # For testing or when password is stored in plain text
        if user.hashed_password == password:
            return user
            
        # Verify hashed password
        if not security.verify_password(password, user.hashed_password):
            return None
            
        return user

    def update(
        self,
        db: Session,
        *,
        db_obj: UserModel,
        obj_in: Union[UserUpdate, Dict[str, Any]],
    ) -> UserModel:
        """Update a user (synchronous)."""
        if isinstance(obj_in, dict):
            update_data = obj_in.copy()
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # Handle password update
        if "password" in update_data:
            hashed_password = security.get_password_hash(update_data["password"])
            update_data["hashed_password"] = hashed_password
            del update_data["password"]
            
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    async def update_async(
        self,
        db: AsyncSession,
        *,
        db_obj: UserModel,
        obj_in: Union[UserUpdate, Dict[str, Any]],
    ) -> UserModel:
        """Update a user (asynchronous)."""
        if isinstance(obj_in, dict):
            update_data = obj_in.copy()
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # Handle password update
        if "password" in update_data:
            hashed_password = security.get_password_hash(update_data["password"])
            update_data["hashed_password"] = hashed_password
            del update_data["password"]

        return await super().update_async(db, db_obj=db_obj, obj_in=update_data)

    def add_role(self, db: Session, *, user_id: int, role_id: int) -> bool:
        """Add a role to a user (synchronous)."""
        from app.models import Role
        
        user = self.get(db, id=user_id, options=[selectinload(UserModel.roles)])
        role = db.get(Role, role_id)
        
        if not user or not role:
            return False
            
        if role not in user.roles:
            user.roles.append(role)
            db.commit()
            db.refresh(user)
            
        return True

    async def add_role_async(self, db: AsyncSession, *, user_id: int, role_id: int) -> bool:
        """Add a role to a user (asynchronous)."""
        from app.models import Role
        
        user = await self.get_async(db, id=user_id)
        if not user:
            return False
            
        result = await db.execute(select(Role).where(Role.id == role_id))
        role = result.scalars().first()
        
        if not role:
            return False
            
        # Refresh user with roles loaded
        result = await db.execute(
            select(UserModel)
            .where(UserModel.id == user_id)
            .options(selectinload(UserModel.roles))
        )
        user = result.scalars().first()
        
        if role not in user.roles:
            user.roles.append(role)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
        return True


# Create a singleton instance
user = CRUDUser(UserModel)
