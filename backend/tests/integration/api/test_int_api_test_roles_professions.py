"""Tests d'intégration pour les endpoints de rôles et professions."""

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models import Role, Profession, EliteSpecialization
from tests.integration.fixtures.factories import (
    UserFactory,
    RoleFactory,
    ProfessionFactory,
    EliteSpecializationFactory,
)


class TestRoles:
    def test_create_role(self, client: TestClient, db: Session):
        # Créer un admin
        admin = UserFactory(is_superuser=True)
        db.add(admin)
        db.commit()

        token = create_access_token(subject=admin.email)

        # Données de test
        role_data = {
            "name": "New Role",
            "description": "Test Role Description",
            "icon_url": "http://example.com/icon.png",
        }

        # Tester la création
        response = client.post(
            "/api/v1/roles/",
            json=role_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == role_data["name"]
        assert data["description"] == role_data["description"]

        # Vérifier en base
        role = db.query(Role).filter(Role.name == role_data["name"]).first()
        assert role is not None
        assert role.description == role_data["description"]

    def test_list_roles(self, client: TestClient, db: Session):
        # Créer des rôles de test
        roles = [RoleFactory() for _ in range(3)]
        db.add_all(roles)
        db.commit()

        # Créer un utilisateur normal
        user = UserFactory()
        db.add(user)
        db.commit()

        token = create_access_token(subject=user.email)

        # Tester la liste
        response = client.get(
            "/api/v1/roles/", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= len(roles)  # Peut y avoir d'autres rôles dans la base
        role_names = {role.name for role in roles}
        assert all(r["name"] in role_names for r in data if r["name"] in role_names)

    def test_update_role(self, client: TestClient, db: Session):
        # Créer un admin et un rôle
        admin = UserFactory(is_superuser=True)
        role = RoleFactory()
        db.add_all([admin, role])
        db.commit()

        token = create_access_token(subject=admin.email)

        # Mettre à jour le rôle
        update_data = {"description": "Updated Description"}
        response = client.put(
            f"/api/v1/roles/{role.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == update_data["description"]

        # Vérifier la mise à jour en base
        db.refresh(role)
        assert role.description == update_data["description"]

    def test_delete_role(self, client: TestClient, db: Session):
        # Créer un admin et un rôle
        admin = UserFactory(is_superuser=True)
        role = RoleFactory()
        db.add_all([admin, role])
        db.commit()
        role_id = role.id

        token = create_access_token(subject=admin.email)

        # Supprimer le rôle
        response = client.delete(
            f"/api/v1/roles/{role_id}", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK

        # Vérifier la suppression en base
        role = db.query(Role).filter(Role.id == role_id).first()
        assert role is None


class TestProfessions:
    def test_create_profession(self, client: TestClient, db: Session):
        # Créer un admin
        admin = UserFactory(is_superuser=True)
        db.add(admin)
        db.commit()

        token = create_access_token(subject=admin.email)

        # Données de test
        profession_data = {
            "name": "New Profession",
            "description": "Test Profession Description",
            "icon_url": "http://example.com/profession.png",
        }

        # Tester la création
        response = client.post(
            "/api/v1/professions/",
            json=profession_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == profession_data["name"]

        # Vérifier en base
        profession = (
            db.query(Profession)
            .filter(Profession.name == profession_data["name"])
            .first()
        )
        assert profession is not None
        assert profession.description == profession_data["description"]

    def test_list_professions(self, client: TestClient, db: Session):
        # Créer des professions de test
        professions = [ProfessionFactory() for _ in range(3)]
        db.add_all(professions)
        db.commit()

        # Créer un utilisateur normal
        user = UserFactory()
        db.add(user)
        db.commit()

        token = create_access_token(subject=user.email)

        # Tester la liste
        response = client.get(
            "/api/v1/professions/", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= len(professions)
        profession_names = {p.name for p in professions}
        assert all(
            p["name"] in profession_names for p in data if p["name"] in profession_names
        )


class TestEliteSpecializations:
    def test_create_elite_specialization(self, client: TestClient, db: Session):
        # Créer un admin et une profession
        admin = UserFactory(is_superuser=True)
        profession = ProfessionFactory()
        db.add_all([admin, profession])
        db.commit()

        token = create_access_token(subject=admin.email)

        # Données de test
        spec_data = {
            "name": "New Elite Spec",
            "profession_id": profession.id,
            "description": "Test Elite Spec",
            "icon_url": "http://example.com/elite.png",
        }

        # Tester la création
        response = client.post(
            "/api/v1/elite-specializations/",
            json=spec_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == spec_data["name"]
        assert data["profession_id"] == profession.id

        # Vérifier en base
        spec = (
            db.query(EliteSpecialization)
            .filter(EliteSpecialization.name == spec_data["name"])
            .first()
        )
        assert spec is not None
        assert spec.profession_id == profession.id

    def test_list_elite_specializations(self, client: TestClient, db: Session):
        # Créer une profession avec des spécialisations
        profession = ProfessionFactory()
        specs = [EliteSpecializationFactory(profession=profession) for _ in range(3)]
        db.add_all([profession] + specs)
        db.commit()

        # Créer un utilisateur normal
        user = UserFactory()
        db.add(user)
        db.commit()

        token = create_access_token(subject=user.email)

        # Tester la liste par profession
        response = client.get(
            f"/api/v1/professions/{profession.id}/elite-specializations",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == len(specs)
        spec_names = {s.name for s in specs}
        assert all(s["name"] in spec_names for s in data)
