"""
Dépendances de base de données pour FastAPI.

Ce module contient les fonctions de dépendance pour les sessions de base de données.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from .factories import AsyncSessionLocal


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Obtient une session de base de données asynchrone pour les dépendances FastAPI.

    Yields:
        AsyncSession: Une instance de session SQLAlchemy asynchrone
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Alias pour compatibilité
get_db = get_async_db
