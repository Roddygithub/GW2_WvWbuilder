"""
Configuration et optimisation de la base de données.

Ce module configure la connexion à la base de données avec des paramètres optimisés
pour les performances en production et en développement.
"""

import logging
from typing import AsyncGenerator, Dict, Any

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)
from sqlalchemy.pool import NullPool
from sqlalchemy import event
from app.core.config import settings

logger = logging.getLogger(__name__)


def setup_sqlite_pragmas(dbapi_connection, connection_record):
    """Configure les pragmas SQLite pour de meilleures performances."""
    if "sqlite" in str(dbapi_connection):
        cursor = dbapi_connection.cursor()
        try:
            # Activer le mode WAL pour de meilleures performances en écriture
            cursor.execute("PRAGMA journal_mode=WAL")

            # Désactiver le verrouillage synchrone (attention: risque de corruption en cas de crash)
            cursor.execute("PRAGMA synchronous=NORMAL")

            # Augmenter la taille du cache (en pages, 1 page = 4KB)
            cursor.execute("PRAGMA cache_size=-2000")  # ~8MB de cache

            # Activer les clés étrangères
            cursor.execute("PRAGMA foreign_keys=ON")

            # Optimiser pour les écritures rapides
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.execute("PRAGMA mmap_size=30000000000")  # 30GB

            logger.debug("SQLite pragmas configurés avec succès")
        except Exception as e:
            logger.warning(f"Erreur lors de la configuration des pragmas SQLite: {e}")
        finally:
            cursor.close()


def create_db_engine(url: str, **kwargs) -> AsyncEngine:
    """Crée un moteur de base de données asynchrone avec une configuration optimisée.

    Args:
        url: L'URL de connexion à la base de données
        **kwargs: Arguments supplémentaires à passer à create_async_engine

    Returns:
        AsyncEngine: Le moteur de base de données configuré
    """
    is_sqlite = "sqlite" in url

    # Configuration des arguments de connexion
    connect_args: Dict[str, Any] = {}

    if is_sqlite:
        # Configuration spécifique à SQLite
        connect_args.update(
            {
                "check_same_thread": False,
                "timeout": 30,  # Temps d'attente pour obtenir un verrou (secondes)
            }
        )

    # Configuration du pool de connexions
    pool_config = {}

    if "sqlite" in url and "memory" in url:
        # Utiliser NullPool pour SQLite en mémoire pour éviter les problèmes de partage de connexion
        pool_config = {
            "poolclass": NullPool,
        }
    else:
        # Configuration pour les autres bases de données
        pool_config = {
            "pool_size": settings.POOL_SIZE,
            "max_overflow": settings.MAX_OVERFLOW,
            "pool_timeout": 30,  # secondes
            "pool_recycle": 3600,  # secondes
            "pool_pre_ping": True,
        }

    # Création du moteur
    engine = create_async_engine(
        url,
        echo=settings.DEBUG,
        connect_args=connect_args,
        **{**pool_config, **kwargs},
    )

    # Configuration des événements pour SQLite
    if is_sqlite:

        @event.listens_for(engine.sync_engine, "connect")
        def configure_sqlite(dbapi_connection, connection_record):
            setup_sqlite_pragmas(dbapi_connection, connection_record)

    return engine


# Moteur de base de données principal
if settings.TESTING:
    # Utilisation d'une base de données en mémoire partagée pour les tests
    async_database_url = "sqlite+aiosqlite:///file:testdb?mode=memory&cache=shared&uri=true"
else:
    async_database_url = settings.get_async_database_url()

logger.info(f"Connexion à la base de données: {async_database_url}")
engine = create_db_engine(async_database_url)

# Configuration de la session asynchrone avec des paramètres optimisés
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,  # Désactive l'auto-commit pour un meilleur contrôle des transactions
    autoflush=False,  # Désactive l'auto-flush pour de meilleures performances
    bind=engine,
    expire_on_commit=False,  # Empêche l'expiration des objets après le commit
    class_=AsyncSession,
    twophase=False,  # Désactive le verrouillage à deux phases pour de meilleures performances
    future=True,  # Active le comportement futur de SQLAlchemy 2.0
)

# Configuration pour les tests
TestSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,  # Utilise le moteur principal configuré pour les tests
    expire_on_commit=False,
)


# Contexte de transaction pour les opérations groupées
class Transaction:
    """Contexte de transaction pour gérer les opérations de base de données."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.transaction = None

    async def __aenter__(self):
        self.transaction = await self.session.begin()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.transaction.rollback()
            logger.error("Erreur de transaction, rollback effectué", exc_info=(exc_type, exc_val, exc_tb))
            return False

        try:
            await self.transaction.commit()
            logger.debug("Transaction validée avec succès")
            return True
        except Exception:
            await self.transaction.rollback()
            logger.error("Erreur lors de la validation de la transaction", exc_info=True)
            raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Fournit une session de base de données pour les dépendances FastAPI.

    Utilisation:
        async with get_db() as db:
            # Utiliser la session db ici
            result = await db.execute(select(...))
    """
    async with AsyncSessionLocal() as session:
        try:
            # Désactive l'expiration automatique des objets après le commit
            session.expire_on_commit = False

            # Active les logs de requêtes en mode debug
            if settings.DEBUG:
                import logging

                logging.basicConfig()
                logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            logger.error("Erreur de session de base de données", exc_info=True)
            raise
        finally:
            await session.close()


# Fonction utilitaire pour les transactions
def transaction() -> Transaction:
    """Crée un nouveau contexte de transaction."""
    return Transaction(AsyncSessionLocal())


async def close_db() -> None:
    """Ferme les connexions à la base de données."""
    await engine.dispose()


async def init_db() -> None:
    """Initialise la base de données avec les tables nécessaires."""
    from app.models.base import Base

    async with engine.begin() as conn:
        # Crée toutes les tables qui n'existent pas encore
        await conn.run_sync(Base.metadata.create_all)


# Configuration de la session asynchrone pour les tests
TestAsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,  # Utilise le moteur principal configuré pour les tests
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    """Fournit une session de test pour les tests."""
    async with TestAsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
