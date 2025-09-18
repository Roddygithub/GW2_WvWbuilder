"""
Configuration de base pour la base de données SQLAlchemy.

Ce module configure la connexion à la base de données et fournit la session de base de données.
"""
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.config import get_settings
from app.models import Base  # Import de la classe de base des modèles

# Obtenir la configuration
settings = get_settings()

# URL de connexion à la base de données
SQLALCHEMY_DATABASE_URL = settings.get_database_url()

# Créer le moteur de base de données
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

# Créer une fabrique de sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Fournit une session de base de données pour les dépendances FastAPI.
    
    Yields:
        Session: Une session de base de données SQLAlchemy.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
