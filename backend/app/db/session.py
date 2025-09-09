"""
Gestion des sessions de base de données SQLAlchemy 2.0.

Ce module fournit la configuration de base pour la gestion des sessions de base de données
et l'initialisation de la base de données avec SQLAlchemy 2.0.
"""
from __future__ import annotations

from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.models.base import Base  # Import de la classe de base des modèles

# URL de base de données
DATABASE_URL = settings.get_database_url()
ASYNC_DATABASE_URL = settings.get_async_database_url()

# Moteur synchrone
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Moteur asynchrone
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in ASYNC_DATABASE_URL else {}
)

# Session locale synchrone
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
    expire_on_commit=False
)

# Session locale asynchrone
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


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


def init_db() -> None:
    """
    Initialise la base de données en créant toutes les tables.
    
    Cette fonction est principalement utilisée pour les tests et l'initialisation
    du développement. En production, utilisez les migrations Alembic.
    """
    # Cette importation est nécessaire pour que SQLAlchemy découvre tous les modèles
    # et crée les tables correspondantes dans la base de données.
    from app.models import (
        User, Role, Profession, EliteSpecialization,
        Composition, CompositionTag, Build, BuildProfession
    )  # noqa: F401
    
    # Création de toutes les tables définies dans les modèles
    Base.metadata.create_all(bind=engine)
    
    # Ajoutez ici toute logique d'initialisation supplémentaire si nécessaire
    # Par exemple, création d'utilisateurs ou de rôles par défaut
