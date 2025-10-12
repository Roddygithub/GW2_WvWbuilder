"""
Gestion des sessions de base de données SQLAlchemy 2.0.

Ce module fournit la configuration de base pour la gestion des sessions de base de données
et l'initialisation de la base de données avec SQLAlchemy 2.0.
"""

from __future__ import annotations

import logging
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
    sync_url = settings.get_database_url()
    async_url = settings.get_async_database_url()

    # Configuration spécifique pour SQLite
    connect_args = {}
    if "sqlite" in sync_url:
        connect_args = {"check_same_thread": False}
        if "memory" in sync_url:
            connect_args["uri"] = True

    engine = create_engine(sync_url, connect_args=connect_args)

    # Configuration pour le moteur asynchrone
    if "sqlite" in async_url and "aiosqlite" in async_url:
        # Utilisation d'une URL simplifiée pour SQLite en mémoire
        async_engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            connect_args={"check_same_thread": False},
            echo=settings.DEBUG,
            poolclass=None,  # Désactive le pool pour SQLite en mémoire
        )
    else:
        async_engine = create_async_engine(async_url, echo=settings.DEBUG)

# Import de la classe de base des modèles
from app.models.base import Base

# Configure logging
logger = logging.getLogger(__name__)


def init_db() -> None:
    """
    Initialise la base de données en créant toutes les tables.
    Cette fonction est principalement utilisée pour les tests et l'initialisation
    du développement. En production, utilisez les migrations Alembic.
    """

    logger.info("Initialisation de la base de données...")

    # Création des tables
    Base.metadata.create_all(bind=engine)

    logger.info("Base de données initialisée avec succès")


async def init_async_db() -> None:
    """
    Initialise la base de données de manière asynchrone en créant toutes les tables.
    Cette fonction est principalement utilisée pour les tests et l'initialisation
    du développement avec des opérations asynchrones.
    """

    logger.info("Initialisation asynchrone de la base de données...")

    # Création des tables de manière asynchrone
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Base de données asynchrone initialisée avec succès")


# Création des fabriques de sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession, expire_on_commit=False
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
