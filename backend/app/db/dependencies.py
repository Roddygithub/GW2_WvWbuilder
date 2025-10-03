"""
Dépendances de base de données pour FastAPI.

Ce module contient les fonctions de dépendance pour les sessions de base de données.
"""
from typing import Generator

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from .factories import SessionLocal, AsyncSessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Obtient une session de base de données synchrone pour les dépendances FastAPI.

    Yields:
        Session: Une instance de session SQLAlchemy synchrone
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> Generator[AsyncSession, None, None]:
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
