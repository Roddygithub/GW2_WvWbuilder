"""
Utilitaires pour la gestion de la base de données.

Ce module fournit des fonctions utilitaires pour gérer les migrations, les sauvegardes
et d'autres opérations courantes sur la base de données.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.database import engine, TestAsyncSessionLocal

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Classe utilitaire pour gérer les opérations sur la base de données."""

    def __init__(self, engine: AsyncEngine):
        """Initialise le gestionnaire de base de données.

        Args:
            engine: Le moteur de base de données SQLAlchemy à utiliser
        """
        self.engine = engine
        self.is_sqlite = "sqlite" in str(engine.url)

    async def get_database_size(self) -> int:
        """Retourne la taille de la base de données en octets."""
        if self.is_sqlite:
            # Pour SQLite, on récupère la taille du fichier
            db_path = self.engine.url.database
            if db_path == ":memory:":
                return 0
            return Path(db_path).stat().st_size
        else:
            # Pour PostgreSQL/MySQL, on utilise des requêtes spécifiques
            async with self.engine.connect() as conn:
                if "postgresql" in str(self.engine.url):
                    result = await conn.execute(text("SELECT pg_database_size(current_database())"))
                    return result.scalar()
                else:
                    # MySQL/MariaDB
                    result = await conn.execute(
                        text(
                            "SELECT SUM(data_length + index_length) "
                            "FROM information_schema.tables "
                            "WHERE table_schema = DATABASE()"
                        )
                    )
                    return result.scalar() or 0

    async def get_table_sizes(self) -> Dict[str, int]:
        """Retourne la taille de chaque table de la base de données."""
        if self.is_sqlite:
            # SQLite ne fournit pas directement cette information
            return {"sqlite": await self.get_database_size()}

        async with self.engine.connect() as conn:
            if "postgresql" in str(self.engine.url):
                result = await conn.execute(
                    text(
                        """
                    SELECT 
                        table_name,
                        pg_total_relation_size('"' || table_name || '"')
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY 2 DESC;
                """
                    )
                )
                return {row[0]: row[1] for row in result.fetchall()}
            else:
                # MySQL/MariaDB
                result = await conn.execute(
                    text(
                        """
                    SELECT 
                        table_name,
                        data_length + index_length as size
                    FROM information_schema.tables
                    WHERE table_schema = DATABASE()
                    ORDER BY size DESC;
                """
                    )
                )
                return {row[0]: row[1] for row in result.fetchall()}

    async def backup_database(self, backup_dir: str = "backups") -> Optional[Path]:
        """Crée une sauvegarde de la base de données.

        Args:
            backup_dir: Le répertoire où sauvegarder le fichier

        Returns:
            Le chemin vers le fichier de sauvegarde créé, ou None en cas d'échec
        """
        if self.is_sqlite:
            db_path = self.engine.url.database
            if db_path == ":memory:":
                logger.warning("Impossible de sauvegarder une base de données en mémoire")
                return None

            backup_dir_path = Path(backup_dir)
            backup_dir_path.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir_path / f"backup_{timestamp}.db"

            import shutil

            shutil.copy2(db_path, backup_path)
            logger.info(f"Sauvegarde créée: {backup_path}")
            return backup_path
        else:
            logger.warning("La sauvegarde automatique n'est pas implémentée pour ce type de base de données")
            return None

    async def optimize_database(self) -> Dict[str, Any]:
        """Optimise la base de données.

        Returns:
            Un dictionnaire contenant les résultats de l'optimisation
        """
        results = {"status": "success", "operations": []}

        try:
            async with self.engine.connect() as conn:
                if self.is_sqlite:
                    # Pour SQLite, on exécute VACUUM et ANALYZE
                    await conn.execute(text("VACUUM"))
                    await conn.execute(text("ANALYZE"))
                    results["operations"].extend(["VACUUM", "ANALYZE"])
                elif "postgresql" in str(self.engine.url):
                    # Pour PostgreSQL, on utilise VACUUM ANALYZE
                    await conn.execute(text("VACUUM ANALYZE"))
                    results["operations"].append("VACUUM ANALYZE")
                else:
                    # Pour MySQL/MariaDB, on utilise OPTIMIZE TABLE
                    result = await conn.execute(text("SHOW TABLES"))
                    tables = [row[0] for row in result.fetchall()]
                    for table in tables:
                        await conn.execute(text(f"OPTIMIZE TABLE {table}"))
                        results["operations"].append(f"OPTIMIZE {table}")

                await conn.commit()
                logger.info("Optimisation de la base de données terminée")

        except Exception as e:
            results["status"] = f"error: {str(e)}"
            logger.error("Erreur lors de l'optimisation de la base de données", exc_info=True)

        return results


# Instances globales pour une utilisation facile
db_manager = DatabaseManager(engine)


# Création d'une instance du gestionnaire pour les tests
async def get_test_db_manager() -> DatabaseManager:
    """Crée une instance de DatabaseManager pour les tests."""
    async with TestAsyncSessionLocal() as session:
        return DatabaseManager(session.get_bind())


# Instance pour les tests (à utiliser avec précaution, préférez get_test_db_manager dans les tests)
test_db_manager = DatabaseManager(engine)
