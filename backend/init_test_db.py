"""
Script pour initialiser la base de données de test.
"""
import asyncio
from sqlalchemy import text
from app.db.session import SessionLocal, async_engine, Base

def init_db():
    """Initialise la base de données de manière synchrone."""
    # Supprimer toutes les tables existantes
    Base.metadata.drop_all(bind=SessionLocal().bind)
    
    # Créer toutes les tables
    Base.metadata.create_all(bind=SessionLocal().bind)
    
    print("Base de données de test initialisée avec succès.")

if __name__ == "__main__":
    init_db()
