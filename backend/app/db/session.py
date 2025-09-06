"""
Gestion des sessions de base de données SQLAlchemy.

Ce module fournit la configuration de base pour la gestion des sessions de base de données
et l'initialisation de la base de données.
"""
from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.base import Base  # Import de la classe de base des modèles


def get_engine():
    """Crée et retourne une instance du moteur SQLAlchemy."""
    db_url = settings.get_database_url()
    connect_args = {}
    
    # Configuration spécifique pour SQLite
    if "sqlite" in db_url:
        connect_args["check_same_thread"] = False
    
    # Création du moteur avec des paramètres optimisés
    return create_engine(
        db_url,
        pool_pre_ping=True,  # Vérifie la connexion avant d'utiliser une connexion du pool
        connect_args=connect_args
    )


# Création de l'instance du moteur
engine = get_engine()

# Configuration de la fabrique de sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Évite les problèmes de session expirée après commit
)


def get_db() -> Generator:
    """
    Génère une session de base de données pour les dépendances FastAPI.
    
    Cette fonction est utilisée comme dépendance dans les routes FastAPI pour obtenir
    une session de base de données. La session est automatiquement fermée après utilisation.
    
    Yields:
        Session: Une session de base de données SQLAlchemy.
        
    Exemple d'utilisation:
        ```python
        from fastapi import Depends
        from sqlalchemy.orm import Session
        
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
        ```
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
