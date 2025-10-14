#!/usr/bin/env python3
"""
Script de seed pour créer l'utilisateur de test frontend@user.com.

Ce script est idempotent : il ne créera l'utilisateur que s'il n'existe pas déjà.
Utilisable localement via :
    cd backend
    poetry run python scripts/seed_test_user.py
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire backend au path pour les imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.role import Role
from app.core.security.password_utils import get_password_hash

# Configuration de l'utilisateur de test
EMAIL = "frontend@user.com"
USERNAME = "frontend"
PASSWORD = "Frontend123!"
DEFAULT_ROLE_NAME = "user"  # Adapter si vous utilisez 'player' ou 'member'


async def seed():
    """Crée l'utilisateur de test si absent."""
    async with AsyncSessionLocal() as session:
        try:
            # Vérifier si l'utilisateur existe déjà
            q = select(User).where(User.email == EMAIL)
            res = await session.execute(q)
            user = res.scalars().first()
            
            if user:
                print(f"✓ User already exists: {EMAIL}")
                print(f"  Username: {user.username}")
                print(f"  ID: {user.id}")
                return

            # Créer l'utilisateur
            hashed = get_password_hash(PASSWORD)
            new_user = User(
                username=USERNAME,
                email=EMAIL,
                hashed_password=hashed,
                is_active=True,
                is_superuser=False,
            )
            session.add(new_user)
            await session.flush()  # Obtenir l'ID de l'utilisateur

            # Attacher le rôle par défaut si la table roles existe
            qrole = select(Role).where(Role.name == DEFAULT_ROLE_NAME)
            resr = await session.execute(qrole)
            role = resr.scalars().first()
            
            if not role:
                # Créer le rôle par défaut s'il n'existe pas
                role = Role(
                    name=DEFAULT_ROLE_NAME,
                    description="Default user role",
                    permission_level=0,
                    is_default=True,
                )
                session.add(role)
                await session.flush()
                print(f"✓ Created default role: {DEFAULT_ROLE_NAME}")

            # Associer le rôle à l'utilisateur
            new_user.roles.append(role)
            
            await session.commit()
            
            print(f"✓ Successfully seeded user: {EMAIL}")
            print(f"  Username: {USERNAME}")
            print(f"  Password: {PASSWORD}")
            print(f"  Role: {DEFAULT_ROLE_NAME}")
            print(f"  ID: {new_user.id}")
            
        except Exception as e:
            await session.rollback()
            print(f"✗ Error seeding user: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Seed Test User Script")
    print("=" * 60)
    asyncio.run(seed())
    print("=" * 60)
    print("Done!")
