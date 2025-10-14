"""Script pour appliquer les migrations de base de données."""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

async def apply_migrations():
    """Applique les migrations de base de données."""
    # Créer une connexion à la base de données
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
    
    async with engine.begin() as conn:
        # Importer la fonction de migration
        from migrations.remove_obsolete_columns import upgrade
        
        # Appliquer la migration
        success = await upgrade(conn)
        
        if success:
            print("✅ Toutes les migrations ont été appliquées avec succès.")
        else:
            print("❌ Une erreur est survenue lors de l'application des migrations.")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(apply_migrations())
