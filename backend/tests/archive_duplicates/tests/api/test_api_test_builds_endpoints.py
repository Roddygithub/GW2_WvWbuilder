"""Tests for the Builds API endpoints."""

import builtins
import os
import sys
import pytest
import pytest_asyncio
from datetime import timedelta

from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select, insert

# Gestion de anext pour Python < 3.10
if not hasattr(builtins, "anext"):
    from async_generator import anext

# Ajout du répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import des modèles et utilitaires
try:
    from app.models import Build, User, Profession, build_profession, Base
    from app.crud.build import build as build_crud
    from app.core.security import get_password_hash, create_access_token
    from app.core.config import settings
    from app.schemas.build import BuildCreate, BuildUpdate
except ImportError as e:
    print(f"Erreur d'import: {e}")
    raise


@pytest.fixture
def app(monkeypatch):
    """
    Create a FastAPI app instance for testing with overrides.
    This ensures we have a clean app instance for each test.
    """
    # Set up test environment variables
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-jwt-secret-key")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")

    from app.main import create_application
    from app.core.config import settings

    # Override settings for testing
    settings.SECRET_KEY = "test-secret-key"
    settings.JWT_SECRET_KEY = "test-jwt-secret-key"
    settings.JWT_ALGORITHM = "HS256"
    settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
    settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30  # For backward compatibility

    # Update the JWT module's settings
    from app.core.security import jwt as jwt_module

    jwt_module.JWT_SECRET_KEY = settings.JWT_SECRET_KEY
    jwt_module.JWT_ALGORITHM = settings.JWT_ALGORITHM
    jwt_module.JWT_ACCESS_TOKEN_EXPIRE_MINUTES = (
        settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    jwt_module.JWT_REFRESH_SECRET_KEY = "test-jwt-refresh-secret-key"
    jwt_module.JWT_REFRESH_TOKEN_EXPIRE_MINUTES = 1440

    app = create_application()
    return app


@pytest.mark.asyncio
async def test_create_build(async_client: AsyncClient, async_session):
    """Test creating a new build directly in the database."""
    # S'assurer que la session est valide
    assert async_session is not None, "La session n'a pas pu être créée"

    # Obtenir la session depuis le générateur
    session = await anext(async_session)

    try:
        print("\n=== DEBUG: Starting test_create_build ===")

        # Create a test user directly in the database
        print("Creating test user...")
        user = User(
            email="test_create@example.com",
            username="testuser_create",
            hashed_password=get_password_hash("testpassword"),
            is_active=True,
            is_superuser=False,
        )
        session.add(user)
        await session.commit()
        print(f"Created user with ID: {user.id}")

        # Create a test profession directly in the database
        print("Creating test profession...")
        profession = Profession(
            name="Test Profession",
            description="A test profession",
            is_active=True,
            icon_url="https://example.com/icon.png",
            game_modes=["wvw", "pve"],
        )
        async_session.add(profession)
        await async_session.commit()
        print(f"Created profession with ID: {profession.id}")

        # Create a test build directly in the database
        print("Creating test build...")
        build = Build(
            name="Test Build",
            description="A test build",
            game_mode="wvw",
            is_public=True,
            team_size=5,
            config={"traits": [1, 2, 3], "skills": [4, 5, 6]},
            created_by_id=user.id,
        )
        async_session.add(build)
        await async_session.commit()
        print(f"Created build with ID: {build.id}")

        # Vérifier que le build a bien un ID
        assert build.id is not None, "Build ID is None after commit"

        # Associate the build with the profession
        print(f"Associating build {build.id} with profession {profession.id}...")
        stmt = insert(build_profession).values(
            build_id=build.id, profession_id=profession.id
        )
        await session.execute(stmt)
        await session.commit()
        print("Association created successfully")

        # Verify the build was created
        print("Verifying build was created...")
        stmt = select(Build).where(Build.id == build.id)
        result = await session.execute(stmt)
        db_build = result.scalar_one_or_none()

        print(f"Retrieved build from database: {db_build}")
        assert db_build is not None, "Build not found in database"
        print(f"Build name: {db_build.name}")
        assert db_build.name == "Test Build"
        print(f"Build description: {db_build.description}")
        assert db_build.description == "A test build"
        print(f"Build game_mode: {db_build.game_mode}")
        assert db_build.game_mode == "wvw"
        print(f"Build is_public: {db_build.is_public}")
        assert db_build.is_public is True
        print(f"Build team_size: {db_build.team_size}")
        assert db_build.team_size == 5
        print(f"Build config: {db_build.config}")
        assert db_build.config == {"traits": [1, 2, 3], "skills": [4, 5, 6]}
        print("Build verification successful")

        # Verify the association with the profession
        print("Verifying build-profession association...")
        stmt = select(build_profession).where(build_profession.c.build_id == build.id)
        result = await session.execute(stmt)
        association = result.first()

        print(f"Retrieved association: {association}")
        assert (
            association is not None
        ), "No association found between build and profession"
        print(f"Association profession_id: {association.profession_id}")
        assert association.profession_id == profession.id
        print("Association verification successful")

        # Return the created build ID for potential use in other tests
        print(f"Test completed successfully. Build ID: {db_build.id}")
        return db_build.id

    except Exception as e:
        await session.rollback()
        print(f"Error in test_create_build: {str(e)}")
        if hasattr(e, "__traceback__"):
            import traceback

            traceback.print_exc()
        raise
    finally:
        # Nettoyer la session
        await session.close()


@pytest.mark.asyncio
async def test_list_builds(async_client: AsyncClient, async_session):
    """Test listing builds with filters."""
    # S'assurer que la session est valide
    assert async_session is not None, "La session n'a pas pu être créée"

    try:
        # Créer un utilisateur de test
        user = User(
            email="test_list@example.com",
            username="testuser_list",
            hashed_password=get_password_hash("testpassword"),
            is_active=True,
            is_superuser=False,
        )
        session = await anext(async_session)
        session.add(user)

        # Créer une profession de test
        profession = Profession(
            name="Test Profession List",
            description="A test profession for listing",
            is_active=True,
            icon_url="https://example.com/icon.png",
            game_modes=["wvw", "pve"],
        )
        session.add(profession)
        await session.commit()

        # Créer un jeton d'authentification
        auth_token = create_access_token(
            subject=str(user.id),
            expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        # Créer un build de test
        build = Build(
            name="Test Build",
            description="A test build",
            game_mode="wvw",
            is_public=True,
            team_size=5,
            created_by_id=user.id,
            config={"skills": [], "traits": []},
            constraints={},
        )
        build.created_by = user  # Définir la relation
        session.add(build)

        await session.commit()

        # Ajouter l'association de profession
        stmt = build_profession.insert().values(
            build_id=build.id, profession_id=profession.id
        )
        await session.execute(stmt)

        # Créer un autre build pour tester le filtrage
        build2 = Build(
            name="Other Build",
            description="Another test build",
            game_mode="pve",
            is_public=True,
            created_by_id=user.id,
            config={"skills": [], "traits": []},
            team_size=5,
            constraints={},
        )
        session.add(build2)
        await session.commit()

        # Ajouter l'association de profession
        stmt = build_profession.insert().values(
            build_id=build2.id, profession_id=profession.id
        )
        await session.execute(stmt)
        await session.commit()

        # Tester la liste non filtrée
        response = await async_client.get(
            "/api/v1/builds/", headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert (
            response.status_code == status.HTTP_200_OK
        ), f"Failed to fetch builds. Status: {response.status_code}, Response: {response.text}"

        data = response.json()
        assert len(data) >= 2, f"Expected at least 2 builds, got {len(data)}"

    except Exception as e:
        await session.rollback()
        print(f"Error in test_list_builds: {str(e)}")
        if hasattr(e, "__traceback__"):
            import traceback

            traceback.print_exc()
        raise
    finally:
        # Nettoyage
        # Ne pas fermer la session ici, elle sera gérée par la fixture
        pass


@pytest.mark.asyncio
async def test_unauthorized_access(async_client: AsyncClient, async_session):
    """Test that unauthorized users cannot modify builds."""
    # S'assurer que la session est valide
    assert async_session is not None, "La session n'a pas pu être créée"

    try:
        # Créer un utilisateur propriétaire
        owner = User(
            email="owner@example.com",
            username="owner",
            hashed_password=get_password_hash("ownerpassword"),
            is_active=True,
            is_superuser=False,
        )
        session = await anext(async_session)
        session.add(owner)

        # Créer un autre utilisateur non autorisé
        other_user = User(
            email="other@example.com",
            username="otheruser",
            hashed_password=get_password_hash("otherpassword"),
            is_active=True,
            is_superuser=False,
        )
        session.add(other_user)

        # Créer une profession de test
        profession = Profession(
            name="Test Profession",
            description="A test profession",
            is_active=True,
            icon_url="https://example.com/icon.png",
            game_modes=["wvw", "pve"],
        )
        session.add(profession)
        await session.commit()

        # Créer un build de test appartenant à owner
        build = Build(
            name="Test Unauthorized Build",
            description="A test build for unauthorized access testing",
            game_mode="wvw",
            is_public=False,  # Le build est privé pour tester l'accès
            team_size=5,
            created_by_id=owner.id,
            config={"skills": [], "traits": []},
            constraints={},
        )
        session.add(build)
        await session.commit()

        # Créer des jetons d'authentification
        owner_token = create_access_token(
            subject=str(owner.id),
            expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        other_user_token = create_access_token(
            subject=str(other_user.id),
            expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        # 1. Tenter de récupérer le build en tant qu'utilisateur non autorisé (doit échouer)
        response = await async_client.get(
            f"/api/v1/builds/{build.id}",
            headers={"Authorization": f"Bearer {other_user_token}"},
        )
        # Doit échouer avec 403 (accès interdit) ou 404 (non trouvé pour la sécurité)
        assert response.status_code in (
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ), f"L'accès non autorisé à un build privé devrait échouer. Code: {response.status_code}"

        # 2. Tenter de mettre à jour le build en tant qu'utilisateur non autorisé
        update_data = {
            "name": "Updated Build Name",
            "description": "Updated description",
        }
        response = await async_client.put(
            f"/api/v1/builds/{build.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {other_user_token}"},
        )
        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "La mise à jour par un utilisateur non autorisé devrait échouer avec 403"

        # 3. Tenter de supprimer le build en tant qu'utilisateur non autorisé
        response = await async_client.delete(
            f"/api/v1/builds/{build.id}",
            headers={"Authorization": f"Bearer {other_user_token}"},
        )
        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "La suppression par un utilisateur non autorisé devrait échouer avec 403"

        # Vérifier que le propriétaire peut toujours accéder à son build
        response = await async_client.get(
            f"/api/v1/builds/{build.id}",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert (
            response.status_code == status.HTTP_200_OK
        ), "Le propriétaire devrait pouvoir accéder à son build"

        # Vérifier que le build n'a pas été modifié par les tentatives non autorisées
        response = await async_client.get(
            f"/api/v1/builds/{build.id}",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        data = response.json()
        assert (
            data["name"] == "Test Unauthorized Build"
        ), "Le nom du build ne devrait pas avoir été modifié"

    except Exception as e:
        await session.rollback()
        print(f"Error in test_unauthorized_access: {str(e)}")
        if hasattr(e, "__traceback__"):
            import traceback

            traceback.print_exc()
        raise
    finally:
        # Nettoyage
        # Ne pas fermer la session ici, elle sera gérée par la fixture
        pass
