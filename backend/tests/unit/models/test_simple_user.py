"""Simple test for the User model."""

import logging
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models import Base, User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///test.db"


@pytest.mark.asyncio
async def test_simple_user():
    """Test simple de création d'utilisateur."""
    # Créer un moteur avec echo=True pour le débogage
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)

    # Supprimer toutes les tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

        # Vérifier que les tables ont été supprimées
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
        logger.info(f"Tables après suppression: {tables}")

        # Créer toutes les tables
        await conn.run_sync(Base.metadata.create_all)

        # Vérifier les tables créées
        result = await conn.execute(text("SELECT name, sql FROM sqlite_master WHERE type='table'"))
        created_tables = {row[0]: row[1] for row in result.fetchall()}
        logger.info(f"Tables créées: {list(created_tables.keys())}")

        # Vérifier que la table users existe
        assert (
            "users" in created_tables
        ), f"La table 'users' n'a pas été créée. Tables créées: {list(created_tables.keys())}"
        logger.info("SQL de création de la table users: %s", created_tables["users"])

    # Créer une session pour insérer un utilisateur
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        try:
            # Créer un utilisateur
            user = User(
                username="testuser",
                email="test@example.com",
                hashed_password="hashed_password",
            )

            # Ajouter à la session et valider
            session.add(user)
            await session.flush()

            # Vérifier que l'utilisateur a un ID
            assert user.id is not None, "L'utilisateur devrait avoir un ID après l'insertion"
            logger.info("Utilisateur créé avec succès, ID: %s", user.id)

            # Annuler la transaction pour ne pas affecter la base de données
            await session.rollback()
        except Exception as e:
            logger.error("Erreur lors de la création de l'utilisateur: %s", str(e))
            raise

    # Nettoyer
    await engine.dispose()

    logger.info("Test réussi !")
