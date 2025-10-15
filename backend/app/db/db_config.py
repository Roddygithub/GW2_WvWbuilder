"""
Configuration de la base de données.

Ce module fournit la configuration de base pour la base de données.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings

# Configuration de la base de données de test
if os.getenv("TESTING", "").lower() == "true":
    # Configuration pour les tests - Utilisation d'une base de données SQLite en mémoire standard
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    ASYNC_SQLALCHEMY_DATABASE_URI = "sqlite+aiosqlite:///:memory:"
else:
    # Configuration pour les environnements de développement et de production
    SQLALCHEMY_DATABASE_URI = settings.SQLALCHEMY_DATABASE_URI
    ASYNC_SQLALCHEMY_DATABASE_URI = settings.ASYNC_SQLALCHEMY_DATABASE_URI


def get_engine_kwargs(is_async: bool = False):
    """
    Obtient la configuration du moteur en fonction du type de base de données.
    """
    kwargs = {}

    # Configuration pour SQLite
    if "sqlite" in (
        ASYNC_SQLALCHEMY_DATABASE_URI if is_async else SQLALCHEMY_DATABASE_URI
    ):
        connect_args = {"check_same_thread": False}

        # Désactiver le pool pour les bases de données en mémoire
        if ":memory:" in (
            ASYNC_SQLALCHEMY_DATABASE_URI if is_async else SQLALCHEMY_DATABASE_URI
        ):
            kwargs["poolclass"] = None

        kwargs.update(
            {
                "connect_args": connect_args,
                "echo": settings.SQL_ECHO,
            }
        )
    # Configuration pour PostgreSQL, MySQL, etc.
    else:
        kwargs.update(
            {
                "pool_pre_ping": getattr(settings, "POOL_PRE_PING", True),
                "pool_recycle": getattr(settings, "POOL_RECYCLE", 3600),
                "pool_size": getattr(settings, "POOL_SIZE", 5),
                "max_overflow": getattr(settings, "MAX_OVERFLOW", 10),
                "pool_timeout": getattr(settings, "POOL_TIMEOUT", 30),
                "echo_pool": getattr(settings, "SQL_ECHO_POOL", False),
            }
        )

    return kwargs


# Moteur de base de données synchrone
engine = create_engine(SQLALCHEMY_DATABASE_URI, **get_engine_kwargs(is_async=False))

# Moteur de base de données asynchrone
async_engine = create_async_engine(
    ASYNC_SQLALCHEMY_DATABASE_URI, **get_engine_kwargs(is_async=True)
)


def init_db():
    """Initialise la base de données en créant toutes les tables."""
    from app.db.base import Base

    Base.metadata.create_all(bind=engine)


async def init_async_db():
    """Initialise la base de données de manière asynchrone en créant toutes les tables."""
    from app.db.base import Base

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
