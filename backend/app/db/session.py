"""
Gestion des sessions de base de données SQLAlchemy 2.0.

Ce module fournit la configuration de base pour la gestion des sessions de base de données
et l'initialisation de la base de données avec SQLAlchemy 2.0.
"""

from __future__ import annotations

from typing import Generator, AsyncGenerator

from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession

# Import des moteurs depuis le module de configuration
try:
    from .db_config import engine, async_engine
except ImportError:
    # Fallback pour les cas où db_config n'est pas encore disponible
    from sqlalchemy import create_engine
    from sqlalchemy.ext.asyncio import create_async_engine
    from app.core.config import settings
    
    # Configuration minimale pour les moteurs
    engine = create_engine(settings.get_database_url())
    async_engine = create_async_engine(settings.get_async_database_url())

# Import de la classe de base des modèles
from app.models.base import Base


def init_db() -> None:
    """
    Initialise la base de données en créant toutes les tables.
    Cette fonction est principalement utilisée pour les tests et l'initialisation
    du développement. En production, utilisez les migrations Alembic.
    """
    import logging

    logger = logging.getLogger(__name__)
    logger.info("Création des tables de la base de données...")

    # Création de toutes les tables définies dans les modèles
    Base.metadata.create_all(bind=engine)

    logger.info("Tables créées avec succès")


# Création des fabriques de sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


def get_db() -> Generator[Session, None, None]:
    """
    Fournit une instance de session de base de données synchrone.
    
    Cette fonction est utilisée comme dépendance dans les routes FastAPI pour obtenir
    une session de base de données. La session est automatiquement fermée après utilisation.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Fournit une instance de session de base de données asynchrone.
    
    Cette fonction est utilisée comme dépendance dans les routes FastAPI pour obtenir
    une session de base de données asynchrone. La session est automatiquement fermée
    après utilisation.
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
