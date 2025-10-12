"""
Comprehensive tests for the Authentication API endpoints.
"""

import uuid
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import User
from app.core.security import verify_password
from jose import jwt

pytestmark = pytest.mark.asyncio


class TestAuthAPI:
    """Test suite for Authentication API endpoints."""

    async def test_login_success(self, async_client: AsyncClient, test_user: User, test_password: str):
        """Test successful user login."""
        # Afficher les détails de l'utilisateur de test
        print("\n=== Détails de l'utilisateur de test ===")
        print(f"ID: {test_user.id}")
        print(f"Email: {test_user.email}")
        print(f"Mot de passe: {test_password}")
        print(f"Mot de passe hashé: {test_user.hashed_password}")
        print(f"Actif: {test_user.is_active}")
        print("==================================\n")

        login_data = {
            "username": test_user.email,
            "password": test_password,  # Utiliser le mot de passe de la fixture
            "grant_type": "password",
        }

        print(f"Données de connexion: {login_data}")
        print(f"URL de la requête: {settings.API_V1_STR}/auth/login")

        # Vérifier que le mot de passe est correct
        from app.core.security import verify_password

        is_password_correct = verify_password(test_password, test_user.hashed_password)
        print(f"Le mot de passe est correct: {is_password_correct}")

        if not is_password_correct:
            print("ERREUR: Le mot de passe ne correspond pas au hash stocké!")

        # Effectuer la requête de connexion
        import time

        start_time = time.time()
        response = await async_client.post(
            f"{settings.API_V1_STR}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        end_time = time.time()

        print(f"Temps de réponse: {end_time - start_time:.2f} secondes")
        print(f"Réponse du serveur: {response.status_code}")
        print(f"Contenu de la réponse: {response.text}")

        # Vérifier que la réponse est valide
        if response.status_code != status.HTTP_200_OK:
            print("\n=== ERREUR D'AUTHENTIFICATION ===")
            print(f"Code d'état: {response.status_code}")
            print(f"Détail: {response.text}")
            print("Vérifiez que l'utilisateur existe bien dans la base de données")
            print("et que le mot de passe est correctement haché.")
            print("===============================\n")

        assert response.status_code == status.HTTP_200_OK, f"Login failed: {response.text}"

        data = response.json()
        assert "access_token" in data, "No access token in response"
        assert data["token_type"] == "bearer", "Invalid token type"
        assert "refresh_token" in data, "No refresh token in response"

        # Vérifier que le token est valide
        try:
            token_data = jwt.decode(
                data["access_token"],
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_aud": False},
            )
            assert token_data["sub"] == str(test_user.id), "Invalid user ID in token"
            assert "exp" in token_data, "Token has no expiration"
        except Exception as e:
            pytest.fail(f"Token validation failed: {str(e)}")

    async def test_login_wrong_password(self, async_client: AsyncClient, test_user: User):
        """Test login with wrong password."""
        login_data = {"username": test_user.email, "password": "wrongpassword", "grant_type": "password"}

        response = await async_client.post(
            f"{settings.API_V1_STR}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), f"Expected status 400, got {response.status_code}: {response.text}"
        assert "Incorrect email or password" in response.text, f"Expected error message not found in: {response.text}"

    async def test_login_nonexistent_user(self, async_client: AsyncClient, caplog):
        """Test login with non-existent user."""
        import logging

        # Enable debug logging
        caplog.set_level(logging.DEBUG)

        login_data = {"username": "nonexistent@example.com", "password": "doesntmatter"}

        # Log the request
        print(f"\nSending login request to: {settings.API_V1_STR}/auth/login")
        print(f"Request data: {login_data}")

        try:
            response = await async_client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)

            # Log the response
            print(f"Response status: {response.status_code}")
            try:
                print(f"Response body: {response.text}")
                print(f"Response JSON: {response.json()}")
            except Exception as e:
                print(f"Could not parse response as JSON: {e}")

            # Log any server errors
            if response.status_code >= 500:
                print("\nServer error details:")
                print(f"Status code: {response.status_code}")
                print(f"Headers: {dict(response.headers)}")
                print(f"Response text: {response.text}")

            # Check the response
            assert (
                response.status_code == status.HTTP_400_BAD_REQUEST
            ), f"Expected status code 400, got {response.status_code}. Response: {response.text}"
            assert (
                "Incorrect email or password" in response.text
            ), f"Expected 'Incorrect email or password' in response, got: {response.text}"

        except Exception as e:
            print(f"\nException during test: {str(e)}")
            print(f"Exception type: {type(e).__name__}")
            import traceback

            traceback.print_exc()
            raise

    async def test_use_access_token(self, async_client: AsyncClient, test_user: User, test_password: str):
        """Test using the access token to access a protected endpoint."""
        # 1. Obtenir un token d'accès
        login_data = {"username": test_user.email, "password": test_password, "grant_type": "password"}

        # 2. Effectuer la requête de connexion
        token_response = await async_client.post(
            f"{settings.API_V1_STR}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # 3. Vérifier que la connexion a réussi
        assert token_response.status_code == status.HTTP_200_OK, f"Login failed: {token_response.text}"

        token_data = token_response.json()
        assert "access_token" in token_data, f"No access_token in response: {token_data}"

        access_token = token_data["access_token"]

        # 4. Utiliser le token pour accéder à une route protégée
        response = await async_client.get(
            f"{settings.API_V1_STR}/users/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        # 5. Vérifier que l'accès est autorisé
        assert response.status_code == status.HTTP_200_OK, f"Failed to access protected endpoint: {response.text}"

        data = response.json()
        assert data["email"] == test_user.email, f"Unexpected user data: {data}"

        # 6. Tester avec un token invalide
        response = await async_client.get(
            f"{settings.API_V1_STR}/users/me",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code in [401, 403], f"Expected 401/403 with invalid token, got {response.status_code}"

        # 7. Tester sans token
        response = await async_client.get(f"{settings.API_V1_STR}/users/me")
        assert response.status_code in [401, 403], f"Expected 401/403 without token, got {response.status_code}"

    @pytest.mark.skip(reason="Refresh token endpoint not yet implemented")
    async def test_refresh_token(self, async_client: AsyncClient, test_user: User):
        """Test refreshing an access token."""
        # This test is skipped as the refresh token endpoint is not yet implemented
        pass

    @pytest.mark.skip(reason="Password reset endpoints not yet implemented")
    async def test_reset_password(self, async_client: AsyncClient, test_user: User):
        """Test password reset flow."""
        # This test is skipped as password reset endpoints are not yet implemented
        pass

    async def test_register_user(self, async_client: AsyncClient, async_db: AsyncSession):
        """Test user registration with proper transaction handling."""
        # Generate unique test data
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"testuser_{unique_id}@example.com"
        test_username = f"testuser_{unique_id}"
        test_password = "TestPassword123!"  # Mot de passe plus sécurisé

        # Test data
        user_data = {
            "email": test_email,
            "username": test_username,
            "password": test_password,
        }

        # Test 1: Inscription réussie
        response = await async_client.post(f"{settings.API_V1_STR}/auth/register", json=user_data)

        assert response.status_code == status.HTTP_201_CREATED, f"Registration failed: {response.text}"

        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "hashed_password" not in data

        # Vérifier que l'utilisateur a été créé dans la base de données
        result = await async_db.execute(select(User).where(User.email == test_email))
        db_user = result.scalars().first()

        assert db_user is not None, "User was not created in the database"
        assert db_user.email == test_email
        assert db_user.username == test_username
        assert verify_password(test_password, db_user.hashed_password), "Password was not hashed correctly"

        # Test 2: Tentative d'inscription avec un email déjà utilisé
        response = await async_client.post(f"{settings.API_V1_STR}/auth/register", json=user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.text.lower()

        # Test 3: Données d'inscription invalides
        invalid_data = {"email": "not-an-email", "username": "", "password": "123"}

        response = await async_client.post(f"{settings.API_V1_STR}/auth/register", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
