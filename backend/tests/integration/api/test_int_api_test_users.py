"""Tests d'intégration pour les endpoints utilisateur."""

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
        login_data = {"username": user.email, "password": password}
        response = client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client: TestClient, db: Session):
        # Tester avec des identifiants invalides
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword",
        }
        response = client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Vérifier que la réponse est une erreur 400 (Bad Request) pour des identifiants invalides
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# Tests pour les opérations CRUD sur les utilisateurs
class TestUsers:
    def test_read_users_me(self, client: TestClient, db: Session):
        # Obtenir les en-têtes d'authentification avec l'utilisateur par défaut du client de test
        headers = client.auth_header()

        # Tester la récupération du profil avec le token JWT
        response = client.get("/api/v1/users/me", headers=headers)

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

        response = client.post("/api/v1/users/", json=user_data, headers=headers)

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
        response = client.get(f"/api/v1/users/{user.id}", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == user.id
        assert data["email"] == user.email
        assert "hashed_password" not in data

    def test_update_user(self, client: TestClient, db: Session):
        # Create a test user with a password
        user = UserFactory(hashed_password="testpassword123")
        db.add(user)
        db.commit()
        db.refresh(user)

        # Get authentication headers for the user
        token = create_access_token(subject=user.id)
        headers = {"Authorization": f"Bearer {token}"}

        # Update the profile with a new username
        new_username = f"updated_{user.username}"
        update_data = {"username": new_username}

        # Make the update request
        response = client.put("/api/v1/users/me", json=update_data, headers=headers)

        # Verify the response
        assert (
            response.status_code == status.HTTP_200_OK
        ), f"Expected status code 200, got {response.status_code}. Response: {response.text}"
        data = response.json()
        assert (
            data["username"] == new_username
        ), f"Expected username to be updated to {new_username}, got {data['username']}"

        # Verify the update in the database by making a new request to get the user
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        user_data = response.json()
        assert (
            user_data["username"] == new_username
        ), f"User's username was not updated to {new_username}, got {user_data['username']}"


# Tests pour les rôles utilisateur
class TestUserRoles:
    def test_add_role_to_user(self, client: TestClient, db: Session):
        # Create an admin user who has permission to add roles
        admin = UserFactory(is_superuser=True)
        user = UserFactory()
        role = RoleFactory()
        db.add_all([admin, user, role])
        db.commit()

        # Use admin's token for authorization
        admin_headers = client.auth_header(user=admin)

        # Add role to user
        response = client.post(f"/api/v1/users/{user.id}/roles/{role.id}", headers=admin_headers)

        assert (
            response.status_code == status.HTTP_200_OK
        ), f"Expected status code 200, got {response.status_code}. Response: {response.text}"

        # Verify role was added by making a GET request to get the user's roles
        response = client.get(f"/api/v1/users/{user.id}", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
        user_data = response.json()
        assert any(r["id"] == role.id for r in user_data["roles"]), f"Role {role.id} was not added to user {user.id}"

    def test_remove_role_from_user(self, client: TestClient, db: Session):
        # Create an admin user who has permission to remove roles
        admin = UserFactory(is_superuser=True)
        role = RoleFactory()
        user = UserFactory(roles=[role])
        db.add_all([admin, user, role])
        db.commit()

        # Use admin's token for authorization
        admin_headers = client.auth_header(user=admin)

        # First verify the role is assigned
        response = client.get(f"/api/v1/users/{user.id}", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
        user_data = response.json()
        assert any(
            r["id"] == role.id for r in user_data["roles"]
        ), f"Role {role.id} was not initially assigned to user {user.id}"

        # Remove role from user
        response = client.delete(f"/api/v1/users/{user.id}/roles/{role.id}", headers=admin_headers)

        assert (
            response.status_code == status.HTTP_200_OK
        ), f"Expected status code 200, got {response.status_code}. Response: {response.text}"

        # Verify role was removed by making a GET request to get the user's roles
        response = client.get(f"/api/v1/users/{user.id}", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
        user_data = response.json()
        assert not any(
            r["id"] == role.id for r in user_data["roles"]
        ), f"Role {role.id} was not removed from user {user.id}"
