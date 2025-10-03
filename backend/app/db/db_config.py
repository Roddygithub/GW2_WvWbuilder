"""
Configuration de la base de données.

Ce module fournit la configuration de base pour la base de données.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


def get_engine_kwargs(is_async: bool = False):
    """
    Obtient la configuration du moteur en fonction du type de base de données.
    """
    kwargs = {}

    if settings.DATABASE_TYPE == "sqlite":
        if is_async:
            kwargs.update(
                {
                    "connect_args": {"check_same_thread": False},
                    "echo": settings.SQL_ECHO,
                }
            )
        else:
            kwargs.update(
                {
                    "connect_args": {"check_same_thread": False},
                    "echo": settings.SQL_ECHO,
                }
            )
    else:
        kwargs.update(
            {
                "pool_pre_ping": settings.POOL_PRE_PING,
                "pool_recycle": settings.POOL_RECYCLE,
                "pool_size": settings.POOL_SIZE,
                "max_overflow": settings.MAX_OVERFLOW,
                "pool_timeout": settings.POOL_TIMEOUT,
                "echo_pool": settings.SQL_ECHO_POOL,
            }
        )

    return kwargs


# Moteur synchrone
engine = create_engine(settings.get_database_url(), **get_engine_kwargs(is_async=False))

# Moteur asynchrone
async_engine = create_async_engine(
    settings.get_async_database_url(), **get_engine_kwargs(is_async=True)
)
