"""
Script pour recréer la base de données de test.
"""
import asyncio
from app.db.session import engine, Base

async def init_db():
    # Supprimer toutes les tables existantes
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    # Recréer toutes les tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Fermer la connexion
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())
    print("Base de données de test recréée avec succès.")
