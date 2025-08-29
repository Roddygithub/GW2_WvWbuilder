"""Configuration des fixtures de test pour pytest."""
import os
import tempfile
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base
from app.api.deps import get_db as deps_get_db
from app.main import app

# Configuration pour les tests
TEST_DATABASE_URL = "sqlite:///:memory:"

# Surcharger la configuration pour les tests
settings.TESTING = True
settings.DATABASE_URL = TEST_DATABASE_URL

# Créer un moteur SQLite en mémoire pour les tests
@pytest.fixture(scope="session")
def test_engine():
    # Import models so all tables are registered on Base.metadata
    import app.models.models  # noqa: F401

    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Créer toutes les tables
    Base.metadata.create_all(bind=test_engine)
    
    yield test_engine
    
    # Nettoyage après les tests
    Base.metadata.drop_all(bind=test_engine)

# Session de test
@pytest.fixture
def db_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = TestingSessionLocal()
    
    yield session
    
    session.close()
    try:
        if transaction.is_active:
            transaction.rollback()
    except Exception:
        # Ignore teardown issues if transaction already deassociated
        pass
    connection.close()

# Client de test FastAPI
@pytest.fixture
def client(db_session):
    # Surcharger la dépendance get_db pour utiliser la session de test
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[deps_get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Réinitialiser les surcharges
    app.dependency_overrides.clear()

# Fixture pour les données de test
@pytest.fixture
def test_data():
    """Retourne des données de test pour les tests."""
    return {
        "user": {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "is_active": True,
            "is_superuser": False,
        },
        "role": {
            "name": "test_role",
            "description": "Test Role",
        },
        "profession": {
            "name": "Test Profession",
            "description": "Test Profession Description",
        },
    }
