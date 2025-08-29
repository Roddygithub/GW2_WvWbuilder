"""Tests d'intégration pour les endpoints utilisateur."""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models import User
from tests.integration.fixtures.factories import UserFactory

# Tests pour l'authentification
class TestAuth:
    def test_login_success(self, client: TestClient, db: Session):
        # Créer un utilisateur de test
        password = "testpassword123"
        user = UserFactory(hashed_password=password)
        db.add(user)
        db.commit()
        
        # Tester la connexion
        response = client.post(
            "/api/v1/auth/login",
            data={"username": user.email, "password": password},
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client: TestClient, db: Session):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "nonexistent@example.com", "password": "wrongpassword"},
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

# Tests pour les opérations CRUD sur les utilisateurs
class TestUsers:
    def test_read_users_me(self, client: TestClient, db: Session):
        # Créer un utilisateur et un token
        user = UserFactory()
        db.add(user)
        db.commit()
        
        token = create_access_token(subject=user.email)
        
        # Tester la récupération du profil
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == user.email
        assert "hashed_password" not in data
    
    def test_create_user(self, client: TestClient, db: Session):
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "testpassword123",
        }
        
        response = client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "id" in data
        
        # Vérifier que l'utilisateur existe en base
        user = db.query(User).filter(User.email == user_data["email"]).first()
        assert user is not None
        assert user.username == user_data["username"]
    
    def test_read_user(self, client: TestClient, db: Session):
        # Créer un utilisateur de test
        user = UserFactory()
        db.add(user)
        db.commit()
        
        # Créer un token d'admin
        admin = UserFactory(is_superuser=True)
        db.add(admin)
        db.commit()
        token = create_access_token(subject=admin.email)
        
        # Tester la lecture du profil
        response = client.get(
            f"/api/v1/users/{user.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == user.id
        assert data["email"] == user.email
    
    def test_update_user(self, client: TestClient, db: Session):
        # Créer un utilisateur de test
        user = UserFactory()
        db.add(user)
        db.commit()
        
        token = create_access_token(subject=user.email)
        
        # Mettre à jour le profil
        update_data = {"username": "updated_username"}
        response = client.put(
            f"/api/v1/users/me",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == update_data["username"]
        
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
        
        token = create_access_token(subject=user.email)
        
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
