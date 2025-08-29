"""Tests d'intégration pour les endpoints utilisateur."""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models import User
from tests.integration.fixtures.factories import UserFactory, RoleFactory

# Tests pour l'authentification
class TestAuth:
    def test_login_success(self, client: TestClient, db: Session):
        # Créer un utilisateur de test
        password = "testpassword123"
        user = UserFactory(hashed_password=password)
        db.add(user)
        db.commit()
        
        # Tester la connexion avec des identifiants valides
        login_data = {
            "username": user.email,
            "password": password
        }
        response = client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client: TestClient, db: Session):
        # Tester avec des identifiants invalides
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Vérifier que la réponse est une erreur 400 (Bad Request) pour des identifiants invalides
        assert response.status_code == status.HTTP_400_BAD_REQUEST

# Tests pour les opérations CRUD sur les utilisateurs
class TestUsers:
    def test_read_users_me(self, client: TestClient, db: Session):
        # Obtenir les en-têtes d'authentification avec l'utilisateur par défaut du client de test
        headers = client.auth_header()
        
        # Tester la récupération du profil avec le token JWT
        response = client.get(
            "/api/v1/users/me",
            headers=headers
        )
        
        # Vérifier que la réponse est correcte
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Vérifier que le mot de passe hashé n'est pas inclus dans la réponse
        assert "hashed_password" not in data
    
    def test_create_user(self, client: TestClient, db: Session):
        # Get auth headers for a superuser
        headers = client.auth_header()
        
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "testpassword123",
        }
        
        response = client.post(
            "/api/v1/users/", 
            json=user_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "id" in data
        assert "hashed_password" not in data
        
        # Vérifier que l'utilisateur existe en base
        user = db.query(User).filter(User.email == user_data["email"]).first()
        assert user is not None
        assert user.username == user_data["username"]
    
    def test_read_user(self, client: TestClient, db: Session):
        # Créer un utilisateur de test
        user = UserFactory()
        db.add(user)
        db.commit()
        
        # Créer un admin et obtenir son en-tête d'authentification
        admin = UserFactory(is_superuser=True)
        db.add(admin)
        db.commit()
        
        # Utiliser l'auth_header du client de test avec l'utilisateur admin
        headers = client.auth_header(user=admin)
        
        # Tester la lecture du profil
        response = client.get(
            f"/api/v1/users/{user.id}",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == user.id
        assert data["email"] == user.email
        assert "hashed_password" not in data
    
    def test_update_user(self, client: TestClient, db: Session):
        # Créer un utilisateur de test
        user = UserFactory()
        db.add(user)
        db.commit()
        db.refresh(user)  # S'assurer que l'utilisateur a un ID
        
        # Obtenir les en-têtes d'authentification pour l'utilisateur
        headers = client.auth_header(user=user)
        
        # Mettre à jour le profil
        update_data = {"username": "updated_username"}
        response = client.put(
            "/api/v1/users/me",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
        data = response.json()
        assert data["username"] == update_data["username"], f"Expected username to be updated to {update_data['username']}, got {data['username']}"
        
        # Vérifier la mise à jour en base
        db.refresh(user)
        assert user.username == update_data["username"]

# Tests pour les rôles utilisateur
class TestUserRoles:
    def test_add_role_to_user(self, client: TestClient, db: Session):
        # Créer un utilisateur et un rôle
        user = UserFactory()
        role = RoleFactory()
        db.add_all([user, role])
        db.commit()
        
        token = create_access_token(subject=user.id)
        
        # Ajouter le rôle à l'utilisateur
        response = client.post(
            f"/api/v1/users/{user.id}/roles/{role.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Vérifier l'ajout du rôle
        db.refresh(user)
        assert role in user.roles
    
    def test_remove_role_from_user(self, client: TestClient, db: Session):
        # Créer un utilisateur avec un rôle
        role = RoleFactory()
        user = UserFactory(roles=[role])
        db.add_all([user, role])
        db.commit()
        
        token = create_access_token(subject=user.email)
        
        # Retirer le rôle de l'utilisateur
        response = client.delete(
            f"/api/v1/users/{user.id}/roles/{role.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Vérifier la suppression du rôle
        db.refresh(user)
        assert role not in user.roles
