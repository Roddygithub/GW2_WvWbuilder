"""Script to apply database migrations manually."""
import asyncio
from sqlalchemy import text
from app.db.session import async_engine

async def apply_migration():
    """Apply the migration to remove obsolete columns from team_members table."""
    # Liste des instructions SQL à exécuter séparément
    sql_statements = [
        # Désactiver la vérification des clés étrangères temporairement
        "PRAGMA foreign_keys=off;",
        
        # Créer une nouvelle table sans les colonnes obsolètes
        """
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
        """,
        
        # Copier les données de l'ancienne table vers la nouvelle
        """
        INSERT INTO team_members_new (id, team_id, user_id, role, created_at, updated_at)
        SELECT id, team_id, user_id, role, created_at, updated_at
        FROM team_members;
        """,
        
        # Supprimer l'ancienne table
        "DROP TABLE team_members;",
        
        # Renommer la nouvelle table
        "ALTER TABLE team_members_new RENAME TO team_members;",
        
        # Réactiver la vérification des clés étrangères
        "PRAGMA foreign_keys=on;"
    ]
    
    async with async_engine.begin() as conn:
        # Exécuter chaque instruction SQL séparément
        for sql in sql_statements:
            try:
                await conn.execute(text(sql))
                await conn.commit()
                sql_first_line = sql.strip().split('\n')[0]
                print(f"Successfully executed: {sql_first_line}...")
            except Exception as e:
                print(f"Error executing SQL: {e}")
                await conn.rollback()
                raise
    
    print("Migration applied successfully!")

if __name__ == "__main__":
    asyncio.run(apply_migration())
