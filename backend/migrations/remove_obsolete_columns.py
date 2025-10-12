"""Migration pour supprimer les colonnes obsolètes de la table team_members."""
from sqlalchemy import text

async def upgrade(db_connection):
    """Applique la migration."""
    # Désactiver temporairement les contraintes de clé étrangère
    await db_connection.execute(text("PRAGMA foreign_keys=off;"))
    await db_connection.commit()
    
    try:
        # Créer une nouvelle table sans les colonnes obsolètes
        await db_connection.execute(text("""
        CREATE TABLE team_members_new (
            id INTEGER NOT NULL,
            team_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role VARCHAR(7) NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME,
            PRIMARY KEY (id),
            FOREIGN KEY(team_id) REFERENCES teams (id) ON DELETE CASCADE,
            FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE (team_id, user_id)
        )
        
        """))
        await db_connection.commit()
        
        # Copier les données de l'ancienne table vers la nouvelle
        await db_connection.execute(text("""
        INSERT INTO team_members_new (id, team_id, user_id, role, created_at, updated_at)
        SELECT id, team_id, user_id, role, created_at, updated_at
        FROM team_members
        
        """))
        await db_connection.commit()
        
        # Supprimer l'ancienne table
        await db_connection.execute(text("DROP TABLE team_members;"))
        await db_connection.commit()
        
        # Renommer la nouvelle table
        await db_connection.execute(text("ALTER TABLE team_members_new RENAME TO team_members;"))
        await db_connection.commit()
        
        print("Migration applied successfully!")
        return True
        
    except Exception as e:
        print(f"Error during migration: {e}")
        await db_connection.rollback()
        raise
    
    finally:
        # Réactiver les contraintes de clé étrangère
        await db_connection.execute(text("PRAGMA foreign_keys=on;"))
        await db_connection.commit()
