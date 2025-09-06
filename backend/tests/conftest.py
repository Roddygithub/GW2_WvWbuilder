"""Configuration des fixtures de test pour pytest."""
import os
import tempfile
from typing import AsyncGenerator, Generator

import pytest
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token
from jose import jwt
from pydantic import ValidationError

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
    # Importer les modèles pour qu'ils soient enregistrés dans les métadonnées de Base
    from app.models import Base  # noqa: F401
    from app.models import (  # noqa: F401
        User, Role, Profession, EliteSpecialization,
        Composition, CompositionTag, Build, BuildProfession
    )

    # Utiliser la même configuration que dans app/db/session.py
    from app.db.session import get_engine
    test_engine = get_engine()
    
    # Créer toutes les tables
    Base.metadata.create_all(bind=test_engine)
    
    yield test_engine
    
    # Nettoyage après les tests
    Base.metadata.drop_all(bind=test_engine)

# Session de test
@pytest.fixture
def db_session(test_engine):
    from sqlalchemy.orm import sessionmaker
    from app.db.session import SessionLocal
    
    # Utiliser la même configuration de session que l'application
    connection = test_engine.connect()
    transaction = connection.begin()
    
    # Créer une session avec les mêmes paramètres que dans app/db/session.py
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=connection,
        expire_on_commit=False  # Important pour éviter les problèmes de session expirée
    )
    
    session = TestingSessionLocal()
    
    # S'assurer que la session est propre avant de commencer
    session.expire_all()
    
    yield session
    
    # Nettoyage après le test
    session.expire_all()
    session.close()
    
    try:
        if transaction.is_active:
            transaction.rollback()
    except Exception as e:
        print(f"Error during transaction rollback: {e}")
    finally:
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
    """Fixture pour créer un client de test FastAPI."""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.api.deps import get_db
    from sqlalchemy.orm import Session
    from typing import Generator
    
    # S'assurer que la session est propre avant de commencer
    db_session.expire_all()
    
    # Surcharger la dépendance get_db pour utiliser la session de test
    def override_get_db() -> Generator[Session, None, None]:
        try:
            # Commencer une nouvelle transaction si aucune n'est active
            if not db_session.in_transaction():
                db_session.begin()
            yield db_session
            # S'assurer que les changements sont flushés
            db_session.flush()
        except Exception as e:
            # En cas d'erreur, annuler la transaction
            db_session.rollback()
            raise
        
    # Surcharger les dépendances d'authentification
    def override_get_current_user():
        # Créer un utilisateur de test si nécessaire
        if not hasattr(override_get_current_user, 'test_user'):
            override_get_current_user.test_user = UserFactory()
            db_session.add(override_get_current_user.test_user)
            db_session.commit()
        return override_get_current_user.test_user
    
    def override_get_current_active_user():
        return override_get_current_user()
        
    def override_get_current_active_superuser():
        # Créer un superutilisateur pour les tests
        if not hasattr(override_get_current_active_superuser, 'superuser'):
            override_get_current_active_superuser.superuser = UserFactory(is_superuser=True)
            db_session.add(override_get_current_active_superuser.superuser)
            db_session.commit()
        return override_get_current_active_superuser.superuser
    
    # Appliquer les surcharges de dépendances
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    app.dependency_overrides[get_current_active_superuser] = override_get_current_active_superuser
    
    # Créer le client de test
    with TestClient(app) as test_client:
        # Stocker les utilisateurs de test dans un dictionnaire pour un accès facile
        test_users = {}
        
        # Fonction utilitaire pour obtenir ou créer un utilisateur de test
        def get_or_create_test_user(user=None, **kwargs):
            if user is None:
                user = UserFactory(**kwargs)
                db_session.add(user)
                db_session.commit()
                db_session.refresh(user)
            test_users[user.id] = user
            return user
            
        # Créer l'utilisateur de test par défaut
        test_user = get_or_create_test_user()
        
        # Fonction utilitaire pour générer les en-têtes d'authentification
        def auth_header(user=None):
            if user is None:
                user = test_user
            
            # S'assurer que l'utilisateur est dans le dictionnaire et la base de données
            if user.id not in test_users:
                test_users[user.id] = user
                db_session.add(user)
                db_session.commit()
                db_session.refresh(user)
                
            # Générer un jeton JWT valide
            token = create_access_token(subject=user.id)
            return {"Authorization": f"Bearer {token}"}
            
        # Ajouter les méthodes utilitaires au client de test
        test_client.auth_header = auth_header
        test_client.get_or_create_test_user = get_or_create_test_user
        
        # Définir l'utilisateur par défaut pour les dépendances
        app.dependency_overrides[get_current_user] = lambda: test_user
        
        # Exécuter le test
        try:
            yield test_client
        finally:
            # Nettoyage après le test
            db_session.rollback()
    
    # Nettoyage final après les tests
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
