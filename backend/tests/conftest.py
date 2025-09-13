"""Configuration des fixtures de test pour pytest."""
import os
import tempfile
from typing import AsyncGenerator, Generator

import pytest
from fastapi import Depends, HTTPException, status
from app.core.security import create_access_token
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base
from app.api.deps import get_db as deps_get_db, get_current_user, get_current_active_user, get_current_active_superuser
from app.main import app
from tests.integration.fixtures.factories import (
    UserFactory,
    RoleFactory,
    ProfessionFactory,
    EliteSpecializationFactory,
    CompositionFactory
)

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

# Alias pour la compatibilité avec les tests existants
@pytest.fixture
def db(db_session):
    return db_session

# Configurer les factories pour utiliser la session de test
@pytest.fixture(autouse=True)
def setup_factories(db_session):
    """Configure les factories pour utiliser la session de test."""
    UserFactory._meta.sqlalchemy_session = db_session
    RoleFactory._meta.sqlalchemy_session = db_session
    ProfessionFactory._meta.sqlalchemy_session = db_session
    EliteSpecializationFactory._meta.sqlalchemy_session = db_session
    CompositionFactory._meta.sqlalchemy_session = db_session
    yield
    # Nettoyage après les tests
    for factory in [UserFactory, RoleFactory, ProfessionFactory, EliteSpecializationFactory, CompositionFactory]:
        factory._meta.sqlalchemy_session = None

# Client de test FastAPI
@pytest.fixture
def client(db_session):
    # Surcharger la dépendance get_db pour utiliser la session de test
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Créer un utilisateur de test par défaut
    test_user = UserFactory()
    db_session.add(test_user)
    db_session.commit()
    
    # Surcharger les dépendances d'authentification pour les tests
    def override_get_current_user():
        # Retourne l'utilisateur de test par défaut
        return test_user
        
    def override_get_current_active_user(current_user = Depends(override_get_current_user)):
        return current_user
        
    def override_get_current_active_superuser():
        # Créer un superutilisateur pour les tests
        superuser = UserFactory(is_superuser=True)
        db_session.add(superuser)
        db_session.commit()
        return superuser
    
    # Surcharger les dépendances
    app.dependency_overrides[deps_get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    app.dependency_overrides[get_current_active_superuser] = override_get_current_active_superuser
    
    # Créer le client de test
    with TestClient(app) as test_client:
        # Ajouter un helper pour l'authentification
        def auth_header(user=None):
            if user is None:
                user = test_user
                db_session.add(user)
                db_session.commit()
            token = create_access_token(subject=user.id)
            return {"Authorization": f"Bearer {token}"}
            
        # Ajouter les méthodes d'aide au client
        test_client.auth_header = auth_header
        test_client.test_user = test_user
        
        def clear_auth():
            if hasattr(test_client, 'test_user'):
                delattr(test_client, 'test_user')
                
        test_client.clear_auth = clear_auth
        
        # Set up default auth header
        test_client.headers.update(auth_header())
        
        yield test_client
    
    # Nettoyage après les tests
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
