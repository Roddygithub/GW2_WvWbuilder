"""
Configuration des tests d'intégration.

Ce module contient les fixtures et configurations pour les tests d'intégration
qui nécessitent une base de données ou d'autres services externes.
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Configuration de la base de test
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Surcharger la configuration pour les tests
settings.TESTING = True
settings.DATABASE_URL = TEST_DATABASE_URL

# Créer un moteur asynchrone pour les tests
engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
    poolclass=NullPool,  # Utiliser NullPool pour les tests
)

# Session de test asynchrone
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Client de test HTTP
@pytest.fixture
def client() -> Generator:
    """Client de test HTTP pour les requêtes d'API."""
    with TestClient(app) as c:
        yield c

# Client de test HTTP asynchrone
@pytest.fixture
async def async_client() -> AsyncGenerator:
    """Client de test HTTP asynchrone pour les requêtes d'API."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# Session de base de données de test
@pytest.fixture(scope="function")
async def db() -> AsyncGenerator:
    """Crée une nouvelle connexion de base de données pour chaque test."""
    # Créer toutes les tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Créer une nouvelle session
    async with TestingSessionLocal() as session:
        # Commencer une transaction
        await session.begin()
        
        # Remplacer la dépendance get_db pour utiliser notre session de test
        async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
            try:
                yield session
            finally:
                pass
        
        app.dependency_overrides[get_db] = override_get_db
        
        try:
            yield session
        finally:
            # Annuler la transaction
            await session.rollback()
    
    # Supprimer toutes les tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Fixture pour les données de test
@pytest.fixture(scope="function")
async def test_data(db: AsyncSession):
    """Fournit des données de test communes pour les tests d'intégration."""
    from app.models import User, Role, Profession, EliteSpecialization, Build
    
    # Créer des rôles
    admin_role = Role(name="admin", description="Administrator")
    user_role = Role(name="user", description="Regular User")
    db.add_all([admin_role, user_role])
    await db.commit()
    
    # Créer des professions
    warrior = Profession(name="Warrior", description="A strong fighter")
    guardian = Profession(name="Guardian", description="A holy warrior")
    db.add_all([warrior, guardian])
    await db.commit()
    
    # Créer des spécialisations d'élite
    berserker = EliteSpecialization(
        name="Berserker",
        description="A furious warrior",
        profession_id=warrior.id,
        icon="berserker_icon.png"
    )
    dragonhunter = EliteSpecialization(
        name="Dragonhunter",
        description="A trap-focused guardian",
        profession_id=guardian.id,
        icon="dragonhunter_icon.png"
    )
    db.add_all([berserker, dragonhunter])
    await db.commit()
    
    # Créer des utilisateurs
    admin_user = User(
        email="admin@example.com",
        username="admin",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        is_active=True,
        is_superuser=True,
    )
    test_user = User(
        email="user@example.com",
        username="testuser",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        is_active=True,
        is_superuser=False,
    )
    db.add_all([admin_user, test_user])
    await db.commit()
    
    # Créer des builds de test
    build1 = Build(
        name="Power Berserker",
        description="High DPS build for Berserker",
        is_public=True,
        user_id=test_user.id,
        profession_id=warrior.id,
        elite_spec_id=berserker.id,
        weapons=["Axe", "Axe"],
        skills=["Banner of Strength", "Banner of Discipline"],
        traits={"Strength": [1, 2, 1], "Discipline": [2, 2, 1], "Berserker": [1, 2, 3]},
    )
    build2 = Build(
        name="Dragonhunter Support",
        description="Support build for Dragonhunter",
        is_public=False,
        user_id=admin_user.id,
        profession_id=guardian.id,
        elite_spec_id=dragonhunter.id,
        weapons=["Staff", "Sword/Focus"],
        skills=["""Signet of Courage"", """Mantra of Liberation""],
        traits={"Virtues": [1, 2, 3], "Radiance": [2, 2, 2], "Dragonhunter": [1, 2, 1]},
    )
    db.add_all([build1, build2])
    await db.commit()
    
    # Retourner les données de test
    return {
        "users": {"admin": admin_user, "user": test_user},
        "roles": {"admin": admin_role, "user": user_role},
        "professions": {"warrior": warrior, "guardian": guardian},
        "elite_specs": {"berserker": berserker, "dragonhunter": dragonhunter},
        "builds": {"berserker_build": build1, "dragonhunter_build": build2},
    }

# Fixture pour les jetons d'authentification
@pytest.fixture(scope="function")
async def test_tokens(test_data):
    """Génère des jetons d'accès pour les utilisateurs de test."""
    from app.core.security import create_access_token
    from datetime import timedelta
    
    admin_user = test_data["users"]["admin"]
    test_user = test_data["users"]["user"]
    
    admin_token = create_access_token(
        subject=str(admin_user.id),
        expires_delta=timedelta(minutes=30)
    )
    
    user_token = create_access_token(
        subject=str(test_user.id),
        expires_delta=timedelta(minutes=30)
    )
    
    return {
        "admin": f"Bearer {admin_token}",
        "user": f"Bearer {user_token}",
    }

# Configuration pour les tests asynchrones
@pytest.fixture(scope="session")
def event_loop():
    """Crée une instance de la boucle d'événements pour les tests asynchrones."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# S'assurer que la base de données est propre avant chaque test
@pytest.fixture(autouse=True, scope="function")
async def clean_db(db: AsyncSession):
    """Nettoie la base de données avant chaque test."""
    # Annuler toutes les transactions en cours
    if db.in_transaction():
        await db.rollback()
    
    # Supprimer toutes les données
    for table in reversed(Base.metadata.sorted_tables):
        await db.execute(table.delete())
    
    await db.commit()
    
    yield
    
    # Nettoyage après le test
    if db.in_transaction():
        await db.rollback()
    
    # Supprimer toutes les données
    for table in reversed(Base.metadata.sorted_tables):
        await db.execute(table.delete())
    
    await db.commit()

# Fixture pour les requêtes HTTP authentifiées
@pytest.fixture
def auth_headers(test_tokens):
    """Retourne des en-têtes d'authentification pour les tests d'API."""
    return {
        "admin": {"Authorization": test_tokens["admin"]},
        "user": {"Authorization": test_tokens["user"]},
    }
