"""Configuration des fixtures de test pour pytest."""
import os
import tempfile
import uuid
from typing import AsyncGenerator, Generator

import pytest
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
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
    CompositionFactory,
    BuildFactory,
    create_test_data
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
    from app.models.base_models import (
        User, Role, Profession, EliteSpecialization,
        Composition, CompositionTag, Build
    )
    from sqlalchemy import (
        inspect, Table, Column, Integer, String, Boolean, Text, JSON, 
        ForeignKey, DateTime, text, MetaData, func, event, UniqueConstraint
    )
    from sqlalchemy.engine import Engine
    from sqlalchemy.schema import CreateTable, DropTable
    
    # Créer un nouveau moteur SQLite en mémoire
    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Enable foreign key constraints for SQLite
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    # Drop all tables if they exist
    with test_engine.connect() as conn:
        # Disable foreign key constraints temporarily
        conn.execute(text("PRAGMA foreign_keys=OFF"))
        conn.commit()
        
        # Get all tables
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]
        
        # Drop all tables in reverse order to avoid foreign key constraint issues
        for table in reversed(tables):
            if table != 'sqlite_sequence':  # Skip SQLite internal table
                conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                conn.commit()
    
    # Create all tables in the correct order
    with test_engine.connect() as conn:
        # Enable foreign key constraints
        conn.execute(text("PRAGMA foreign_keys=ON"))
        conn.commit()
        
        # Create a new metadata object to avoid conflicts
        metadata = MetaData()
        
        # Define all tables in the correct order
        Table(
            'users',
            metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('username', String, unique=True, index=True, nullable=False),
            Column('email', String, unique=True, index=True, nullable=False),
            Column('hashed_password', String, nullable=False),
            Column('full_name', String, nullable=True),
            Column('is_active', Boolean, default=True),
            Column('is_superuser', Boolean, default=False),
            Column('created_at', DateTime(timezone=True), server_default=func.now()),
            Column('updated_at', DateTime(timezone=True), onupdate=func.now())
        )
        
        Table(
            'roles',
            metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('name', String, unique=True, index=True, nullable=False),
            Column('description', Text, nullable=True),
            Column('permission_level', Integer, default=0, nullable=False),
            Column('is_default', Boolean, default=False, nullable=False),
            Column('created_at', DateTime(timezone=True), server_default=func.now()),
            Column('updated_at', DateTime(timezone=True), onupdate=func.now())
        )
        
        Table(
            'user_roles',
            metadata,
            Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
            Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
            Column('created_at', DateTime(timezone=True), server_default=func.now())
        )
        
        Table(
            'professions',
            metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('name', String, unique=True, index=True, nullable=False),
            Column('icon_url', String, nullable=True),
            Column('description', Text, nullable=True),
            Column('game_modes', JSON, nullable=True, default=[]),
            Column('created_at', DateTime(timezone=True), server_default=func.now()),
            Column('updated_at', DateTime(timezone=True), onupdate=func.now())
        )
        
        Table(
            'elite_specializations',
            metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('name', String, index=True, nullable=False),
            Column('profession_id', Integer, ForeignKey('professions.id', ondelete='CASCADE'), nullable=False),
            Column('icon_url', String, nullable=True),
            Column('description', Text, nullable=True),
            Column('created_at', DateTime(timezone=True), server_default=func.now()),
            Column('updated_at', DateTime(timezone=True), onupdate=func.now())
        )
        
        Table(
            'builds',
            metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('name', String, index=True, nullable=False),
            Column('description', Text, nullable=True),
            Column('game_mode', String, default="wvw"),
            Column('team_size', Integer, default=5),
            Column('is_public', Boolean, default=False),
            Column('created_by_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
            Column('created_at', DateTime(timezone=True), server_default=func.now()),
            Column('updated_at', DateTime(timezone=True), onupdate=func.now()),
            Column('config', JSON, nullable=False, default=dict),
            Column('constraints', JSON, nullable=True, default=dict)
        )
        
        Table(
            'compositions',
            metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('name', String, index=True, nullable=False),
            Column('description', Text, nullable=True),
            Column('squad_size', Integer, default=10),
            Column('is_public', Boolean, default=True),
            Column('created_by', Integer, ForeignKey('users.id', ondelete='CASCADE')),
            Column('created_at', DateTime(timezone=True), server_default=func.now()),
            Column('updated_at', DateTime(timezone=True), onupdate=func.now()),
            Column('build_id', Integer, ForeignKey('builds.id', ondelete='SET NULL'), nullable=True)
        )
        
        Table(
            'composition_members',
            metadata,
            Column('composition_id', Integer, ForeignKey('compositions.id', ondelete='CASCADE'), primary_key=True),
            Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
            Column('role_id', Integer, ForeignKey('roles.id', ondelete='SET NULL'), nullable=True),
            Column('profession_id', Integer, ForeignKey('professions.id', ondelete='SET NULL'), nullable=True),
            Column('elite_specialization_id', Integer, ForeignKey('elite_specializations.id', ondelete='SET NULL'), nullable=True),
            Column('notes', Text, nullable=True),
            Column('created_at', DateTime(timezone=True), server_default=func.now())
        )
        
        Table(
            'composition_tags',
            metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('name', String, index=True, nullable=False),
            Column('composition_id', Integer, ForeignKey('compositions.id', ondelete='CASCADE')),
            Column('created_at', DateTime(timezone=True), server_default=func.now())
        )
        
        # Finally, create the build_professions table with the correct schema
        Table(
            'build_professions',
            metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('build_id', Integer, ForeignKey('builds.id', ondelete='CASCADE'), nullable=False, index=True),
            Column('profession_id', Integer, ForeignKey('professions.id', ondelete='CASCADE'), nullable=False, index=True),
            Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False),
            UniqueConstraint('build_id', 'profession_id', name='uq_build_profession')
        )
        
        # Create all tables
        metadata.create_all(test_engine)
        
        # Verify all tables were created
        inspector = inspect(test_engine)
        created_tables = inspector.get_table_names()
        print("\nCreated tables:", created_tables)
        
        if 'build_professions' in created_tables:
            print("\nBuildProfessions table structure:")
            for col in inspector.get_columns('build_professions'):
                print(f"- {col['name']}: {col['type']} (PK: {col.get('primary_key', False)})")
        else:
            print("\nERROR: build_professions table was not created!")
    
    # Verify the build_professions table was created correctly
    inspector = inspect(test_engine)
    if 'build_professions' in inspector.get_table_names():
        print("\nBuildProfessions table structure:")
        for col in inspector.get_columns('build_professions'):
            print(f"- {col['name']}: {col['type']} (PK: {col.get('primary_key', False)})")
    
    yield test_engine
    
    # Clean up after tests
    with test_engine.connect() as conn:
        # Disable foreign key constraints for cleanup
        conn.execute(text("PRAGMA foreign_keys=OFF"))
        conn.commit()
        
        # Drop all tables in reverse order
        for table in reversed(Base.metadata.sorted_tables):
            table.drop(bind=test_engine)

# Test database session
@pytest.fixture
def db_session(test_engine):
    from sqlalchemy.orm import sessionmaker
    
    # Create a new session factory bound to the test engine
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    # Create a new session
    db = TestingSessionLocal()
    
    # Begin a nested transaction
    transaction = db.begin_nested()
    
    try:
        yield db
    finally:
        # Rollback the transaction to undo any changes made during the test
        if transaction.is_active:
            transaction.rollback()
        db.close()

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
        # S'assurer que nous avons une nouvelle transaction propre
        if db_session.in_transaction():
            db_session.rollback()
            
        # Commencer une nouvelle transaction
        db_session.begin()
        try:
            yield db_session
            # Valider la transaction si tout s'est bien passé
            db_session.commit()
        except Exception as e:
            # En cas d'erreur, annuler la transaction
            db_session.rollback()
            raise
        finally:
            # Toujours fermer la session pour éviter les fuites de mémoire
            db_session.close()
        
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
            try:
                if user is None:
                    # Créer un utilisateur unique avec un email et un nom d'utilisateur uniques
                    unique_id = str(uuid.uuid4())[:8]
                    user_data = {
                        'email': f'test{unique_id}@example.com',
                        'username': f'testuser{unique_id}',
                        'hashed_password': 'testpassword',
                        'is_active': True,
                        'is_superuser': kwargs.pop('is_superuser', False)
                    }
                    user_data.update(kwargs)
                    user = UserFactory(**user_data)
                    db_session.add(user)
                    db_session.commit()
                    db_session.refresh(user)
                
                test_users[user.id] = user
                return user
            except Exception as e:
                db_session.rollback()
                raise
        
        # Fonction pour effacer l'authentification
        def clear_auth():
            test_client.headers.clear()
            
        # Fonction utilitaire pour générer les en-têtes d'authentification
        def auth_header(user=None, **kwargs):
            if user is None:
                user = get_or_create_test_user(**kwargs)
            
            # S'assurer que l'utilisateur est dans le dictionnaire et la base de données
            if user.id not in test_users:
                db_session.add(user)
                db_session.commit()
                db_session.refresh(user)
                test_users[user.id] = user
            
            # Générer un jeton JWT valide
            token = create_access_token(subject=user.id)
            return {"Authorization": f"Bearer {token}"}
        
        # Créer un utilisateur administrateur par défaut
        admin_user = get_or_create_test_user(
            email='admin@example.com',
            username='admin',
            is_superuser=True
        )
        
        # Créer un utilisateur normal par défaut
        normal_user = get_or_create_test_user(
            email='user@example.com',
            username='normaluser',
            is_superuser=False
        )
        
        # Ajouter les méthodes utilitaires au client de test
        test_client.auth_header = auth_header
        test_client.clear_auth = clear_auth
        test_client.get_or_create_test_user = get_or_create_test_user
        test_client.test_user = normal_user
        test_client.admin_user = admin_user
        
        # Exécuter le test
        try:
            yield test_client
        finally:
            # Clean up after tests
            try:
                # Rollback any pending transactions
                if db_session.in_transaction():
                    db_session.rollback()
                    
                # Clear all data from tables
                for table in reversed(Base.metadata.sorted_tables):
                    db_session.execute(table.delete())
                
                # Reset SQLite sequences if they exist
                try:
                    db_session.execute(text("DELETE FROM sqlite_sequence"))
                except Exception:
                    # Ignore if sqlite_sequence doesn't exist
                    pass
                    
                db_session.commit()
                
            except Exception as e:
                db_session.rollback()
                raise
            finally:
                # Clear dependency overrides
                app.dependency_overrides.clear()
                
                # Close the session
                db_session.close()

# Fixture pour les données de test
@pytest.fixture(scope="function")
def test_data(db_session):
    """Retourne des données de test pour les tests."""
    # Créer les données de test
    data = create_test_data(db_session)
    
    # Ajouter des données de base pour les tests d'API
    data.update({
        "user_credentials": {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
            "full_name": "Test User"
        },
        "admin_credentials": {
            "email": "admin@example.com",
            "username": "admin",
            "password": "adminpass123",
            "full_name": "Admin User"
        },
        "role_data": {
            "name": "test_role",
            "description": "Test role description"
        }
    })
    
    return data
