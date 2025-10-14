#!/usr/bin/env python3
"""
Fix test user username from 'frontenduser' to 'frontend'
"""

import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select, delete, insert
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.user_role import user_roles_table
from app.core.security.password_utils import get_password_hash

EMAIL = "frontend@user.com"
CORRECT_USERNAME = "frontend"
PASSWORD = "Frontend123!"

async def fix_user():
    """Delete and recreate the test user with correct username."""
    async with AsyncSessionLocal() as session:
        try:
            # Delete existing user
            stmt = delete(User).where(User.email == EMAIL)
            await session.execute(stmt)
            await session.commit()
            print(f"✓ Deleted old user with email {EMAIL}")
            
        except Exception as e:
            print(f"Note: No existing user to delete ({e})")
            await session.rollback()
    
    # Now create fresh user with correct username
    async with AsyncSessionLocal() as session:
        try:
            # Create user
            hashed = get_password_hash(PASSWORD)
            new_user = User(
                username=CORRECT_USERNAME,
                email=EMAIL,
                hashed_password=hashed,
                is_active=True,
                is_superuser=False,
            )
            session.add(new_user)
            await session.flush()
            
            # Add default role
            qrole = select(Role).where(Role.name == "user")
            resr = await session.execute(qrole)
            role = resr.scalars().first()
            
            if not role:
                role = Role(
                    name="user",
                    description="Default user role",
                    permission_level=0,
                    is_default=True,
                )
                session.add(role)
                await session.flush()
            
            # Add role via direct insert to avoid lazy-load issues
            await session.execute(
                insert(user_roles_table).values(user_id=new_user.id, role_id=role.id)
            )
            await session.commit()
            
            print(f"✅ Successfully created user:")
            print(f"   Email: {EMAIL}")
            print(f"   Username: {CORRECT_USERNAME}")
            print(f"   Password: {PASSWORD}")
            
        except Exception as e:
            await session.rollback()
            print(f"✗ Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("Fixing Test User")
    print("=" * 60)
    asyncio.run(fix_user())
    print("=" * 60)
    print("Done! User is ready for E2E tests.")
