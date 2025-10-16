"""Script pour initialiser la base de données avec le bon schéma."""
import os
import sys
from pathlib import Path

# Ajouter le répertoire backend au path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, inspect
from app.db.base import Base
from app.models import *  # Import tous les modèles

def init_database():
    """Crée toutes les tables avec le schéma actuel."""
    # URL de la base de données (dans backend/)
    db_path = Path(__file__).parent / "gw2_wvwbuilder.db"
    database_url = f"sqlite:///{db_path}"
    
    print(f"🔧 Création base de données: {db_path}")
    
    # Créer le moteur
    engine = create_engine(database_url, echo=False)
    
    # Créer toutes les tables
    Base.metadata.create_all(bind=engine)
    
    # Vérifier les tables créées
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"✅ {len(tables)} tables créées:")
    for table in sorted(tables):
        columns = [col['name'] for col in inspector.get_columns(table)]
        print(f"   - {table}: {len(columns)} colonnes")
        if table == 'users':
            print(f"     Colonnes: {', '.join(columns)}")
    
    engine.dispose()
    print("\n✅ Base de données initialisée avec succès!")

if __name__ == "__main__":
    init_database()
