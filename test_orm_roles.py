#!/usr/bin/env python3
"""Test ORM role loading"""

import asyncio
import sys
from pathlib import Path

backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import AsyncSessionLocal, engine
from app.models.user import User
from app.core.config import settings


async def test_roles():
    print(f"Database URL: {settings.get_async_database_url()}")
    print(f"Engine URL: {engine.url}")
    
    async with AsyncSessionLocal() as db:
        # Test 1: Load user without selectinload
        print("\n=== Test 1: Without selectinload ===")
        stmt = select(User).where(User.id == 9)
        result = await db.execute(stmt)
        user = result.scalars().first()
        if user:
            print(f"User: {user.username}")
            print(f"Roles (lazy): {user.roles}")
        else:
            print("User not found!")
        
        # Test 2: Load user WITH selectinload
        print("\n=== Test 2: With selectinload ===")
        stmt = select(User).where(User.id == 9).options(selectinload(User.roles))
        result = await db.execute(stmt)
        user = result.scalars().first()
        if user:
            print(f"User: {user.username}")
            print(f"Roles (eager): {user.roles}")
        else:
            print("User not found!")
        
        # Test 3: Check role_associations
        print("\n=== Test 3: Check role_associations ===")
        stmt = select(User).where(User.id == 9).options(selectinload(User.role_associations))
        result = await db.execute(stmt)
        user = result.scalars().first()
        if user:
            print(f"User: {user.username}")
            print(f"Role associations: {user.role_associations}")
        else:
            print("User not found!")


if __name__ == "__main__":
    asyncio.run(test_roles())
