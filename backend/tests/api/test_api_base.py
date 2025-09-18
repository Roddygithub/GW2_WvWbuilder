"""
Tests de base pour les endpoints d'API.

Ces tests vérifient les fonctionnalités de base des endpoints d'API,
comme l'authentification et la validation des requêtes.
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from tests.test_config import TestData, Headers, ExpectedErrors

# Client de test
client = TestClient(app)

class TestAPIBase:
    """Tests de base pour les endpoints d'API."""
    
    def test_health_check(self):
        """Teste l'endpoint de vérification de santé de l'API."""
        response = client.get("/api/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok"}
    
    def test_docs_available(self):
        """Vérifie que la documentation de l'API est disponible."""
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
    
    def test_openapi_schema_available(self):
        """Vérifie que le schéma OpenAPI est disponible."""
        response = client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK
        assert "application/json" in response.headers["content-type"]
        assert "openapi" in response.json()

class TestAuthentication:
    """Tests pour l'authentification de l'API."""
    
    def test_login_success(self, test_user):
        """Teste la connexion avec des identifiants valides."""
        login_data = {
            "username": test_user.email,
            "password": "testpassword123",
        }
        response = client.post(
            "/api/auth/login",
            data=login_data,
            headers=Headers.FORM
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()
        assert "token_type" in response.json()
    
    def test_login_invalid_credentials(self):
        """Teste la connexion avec des identifiants invalides."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword",
        }
        response = client.post(
            "/api/auth/login",
            data=login_data,
            headers=Headers.FORM
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.json()
        assert ExpectedErrors.INVALID_CREDENTIALS in response.json()["detail"]
    
    def test_protected_route_unauthorized(self):
        """Teste l'accès à une route protégée sans authentification."""
        response = client.get("/api/users/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.json()
        assert "Not authenticated" in response.json()["detail"]
    
    def test_protected_route_authorized(self, test_user, test_token):
        """Teste l'accès à une route protégée avec authentification valide."""
        response = client.get(
            "/api/users/me",
            headers=Headers.auth(test_token)
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == str(test_user.id)
        assert response.json()["email"] == test_user.email

class TestValidation:
    """Tests pour la validation des requêtes d'API."""
    
    def test_invalid_json(self):
        """Teste l'envoi d'un JSON invalide."""
        response = client.post(
            "/api/auth/register",
            content="{\"invalid": json}",
            headers=Headers.JSON
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "detail" in response.json()
    
    def test_validation_error(self, test_token):
        """Teste la validation des données de requête."""
        # Données invalides (email manquant)
        user_data = {
            "password": "testpass",
            "full_name": "Test User"
        }
        
        response = client.post(
            "/api/users/",
            json=user_data,
            headers=Headers.auth(test_token)
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "detail" in response.json()
        assert any("field required" in str(err) for err in response.json()["detail"])

class TestErrorHandling:
    """Tests pour la gestion des erreurs de l'API."""
    
    def test_not_found_error(self, test_token):
        """Teste la réponse pour une ressource introuvable."""
        response = client.get(
            "/api/users/00000000-0000-0000-0000-000000000000",
            headers=Headers.auth(test_token)
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "detail" in response.json()
        assert "not found" in response.json()["detail"].lower()
    
    def test_forbidden_error(self, test_user, test_token):
        """Teste l'accès à une ressource non autorisée."""
        # Essayer de mettre à jour un autre utilisateur
        response = client.put(
            f"/api/users/00000000-0000-0000-0000-000000000001",
            json={"email": "newemail@example.com"},
            headers=Headers.auth(test_token)
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "detail" in response.json()
        assert "not enough permissions" in response.json()["detail"].lower()

# Fixtures pour les tests d'API
@pytest.fixture
def test_user(db):
    """Crée un utilisateur de test pour les tests d'API."""
    from app.models.user import User
    
    user = User(
        email=TestData.TEST_USER["email"],
        hashed_password=TestData.TEST_USER["password"],  # Le mot de passe sera hashé par le modèle
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_token(test_user):
    """Génère un jeton d'authentification pour les tests."""
    from app.core.security import create_access_token
    from datetime import timedelta
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(
        subject=str(test_user.id),
        expires_delta=access_token_expires
    )
