"""
Tests d'intégration pour l'API d'authentification.

Ces tests vérifient le bon fonctionnement des endpoints d'authentification.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.core.config import settings
from tests.helpers import (
    create_user,
    random_email,
    random_password,
    get,
    post,
)

pytestmark = pytest.mark.asyncio


class TestAuthAPI:
    """Tests pour l'API d'authentification."""

    async def test_login_success(self, client: TestClient, db_session):
        """Teste la connexion réussie d'un utilisateur."""
        # Créer un utilisateur de test
        password = random_password()
        user = create_user(db=db_session, email=random_email(), password=password, is_active=True, is_verified=True)

        # Tester la connexion
        login_data = {"username": user.email, "password": password}

        response = await post(
            client, f"{settings.API_V1_STR}/auth/login", json=login_data, expected_status=status.HTTP_200_OK
        )

        # Vérifier la réponse
        assert "access_token" in response.json
        assert "token_type" in response.json
        assert response.json["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, client: TestClient, db_session):
        """Teste la tentative de connexion avec des identifiants invalides."""
        # Créer un utilisateur de test
        user = create_user(
            db=db_session, email=random_email(), password=random_password(), is_active=True, is_verified=True
        )

        # Tester avec un mot de passe incorrect
        login_data = {"username": user.email, "password": "wrong_password"}

        response = await post(
            client, f"{settings.API_V1_STR}/auth/login", json=login_data, expected_status=status.HTTP_401_UNAUTHORIZED
        )

        # Vérifier le message d'erreur
        assert "Incorrect email or password" in response.json["detail"]

    async def test_get_current_user(self, client: TestClient, db_session, auth_headers):
        """Teste la récupération des informations de l'utilisateur connecté."""
        response = await get(
            client, f"{settings.API_V1_STR}/users/me", headers=auth_headers, expected_status=status.HTTP_200_OK
        )

        # Vérifier que les informations de l'utilisateur sont renvoyées
        assert "id" in response.json
        assert "email" in response.json
        assert "is_active" in response.json
        assert response.json["is_active"] is True

    async def test_refresh_token(self, client: TestClient, auth_headers):
        """Teste le rafraîchissement du token d'accès."""
        # Obtenir un nouveau token avec le refresh token
        response = await post(
            client,
            f"{settings.API_V1_STR}/auth/refresh-token",
            headers=auth_headers,
            expected_status=status.HTTP_200_OK,
        )

        # Vérifier qu'un nouveau token est renvoyé
        assert "access_token" in response.json
        assert "token_type" in response.json
        assert response.json["token_type"] == "bearer"

        # Vérifier que le nouveau token est valide
        new_token = response.json["access_token"]
        response = await get(
            client,
            f"{settings.API_V1_STR}/users/me",
            headers={"Authorization": f"Bearer {new_token}"},
            expected_status=status.HTTP_200_OK,
        )
        assert "id" in response.json


class TestPasswordReset:
    """Tests pour la réinitialisation du mot de passe."""

    async def test_request_password_reset(self, client: TestClient, db_session):
        """Teste la demande de réinitialisation de mot de passe."""
        # Créer un utilisateur de test
        user = create_user(db=db_session, email=random_email(), is_active=True, is_verified=True)

        # Demander une réinitialisation de mot de passe
        response = await post(
            client,
            f"{settings.API_V1_STR}/auth/forgot-password",
            json={"email": user.email},
            expected_status=status.HTTP_200_OK,
        )

        # Vérifier que la demande a été enregistrée
        assert "message" in response.json
        assert "reset_token" in response.json

    async def test_reset_password(self, client: TestClient, db_session):
        """Teste la réinitialisation du mot de passe avec un token valide."""
        # Créer un utilisateur de test
        user = create_user(db=db_session, email=random_email(), is_active=True, is_verified=True)

        # Générer un token de réinitialisation (dans un environnement réel, ce serait envoyé par email)
        from app.core.security import create_reset_token

        reset_token = create_reset_token(email=user.email)

        # Définir un nouveau mot de passe
        new_password = "NewSecurePass123!"

        # Réinitialiser le mot de passe
        response = await post(
            client,
            f"{settings.API_V1_STR}/auth/reset-password",
            json={"token": reset_token, "new_password": new_password},
            expected_status=status.HTTP_200_OK,
        )

        # Vérifier que le mot de passe a été mis à jour
        assert "message" in response.json

        # Essayer de se connecter avec le nouveau mot de passe
        login_data = {"username": user.email, "password": new_password}

        response = await post(
            client, f"{settings.API_V1_STR}/auth/login", json=login_data, expected_status=status.HTTP_200_OK
        )

        # Vérifier que la connexion est réussie
        assert "access_token" in response.json
