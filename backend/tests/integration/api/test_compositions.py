"""Tests d'intégration pour les endpoints de composition."""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models import Composition, User, Role, Profession, EliteSpecialization
from tests.integration.fixtures.factories import (
    UserFactory, 
    RoleFactory, 
    ProfessionFactory, 
    EliteSpecializationFactory,
    CompositionFactory
)

class TestCompositionCRUD:
    def test_create_composition(self, client: TestClient, db: Session):
        # Créer un utilisateur et un token
        user = UserFactory()
        db.add(user)
        db.commit()
        
        token = create_access_token(subject=user.email)
        
        # Données de test pour la création
        composition_data = {
            "name": "Test Composition",
            "description": "Test Description",
            "squad_size": 10,
            "is_public": True
        }
        
        # Tester la création
        response = client.post(
            "/api/v1/compositions/",
            json=composition_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == composition_data["name"]
        assert data["created_by"] == user.id
        
        # Vérifier en base
        composition = db.query(Composition).filter(Composition.name == composition_data["name"]).first()
        assert composition is not None
        assert composition.created_by == user.id
    
    def test_read_composition(self, client: TestClient, db: Session):
        # Créer une composition de test
        user = UserFactory()
        composition = CompositionFactory(created_by=user.id)
        db.add_all([user, composition])
        db.commit()
        
        token = create_access_token(subject=user.email)
        
        # Tester la lecture
        response = client.get(
            f"/api/v1/compositions/{composition.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == composition.id
        assert data["name"] == composition.name
    
    def test_update_composition(self, client: TestClient, db: Session):
        # Créer une composition de test
        user = UserFactory()
        composition = CompositionFactory(created_by=user.id)
        db.add_all([user, composition])
        db.commit()
        
        token = create_access_token(subject=user.email)
        
        # Mettre à jour la composition
        update_data = {"name": "Updated Name", "description": "Updated Description"}
        response = client.put(
            f"/api/v1/compositions/{composition.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        
        # Vérifier la mise à jour en base
        db.refresh(composition)
        assert composition.name == update_data["name"]
    
    def test_delete_composition(self, client: TestClient, db: Session):
        # Créer une composition de test
        user = UserFactory()
        composition = CompositionFactory(created_by=user.id)
        db.add_all([user, composition])
        db.commit()
        composition_id = composition.id
        
        token = create_access_token(subject=user.email)
        
        # Supprimer la composition
        response = client.delete(
            f"/api/v1/compositions/{composition_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Vérifier la suppression en base
        composition = db.query(Composition).filter(Composition.id == composition_id).first()
        assert composition is None

class TestCompositionMembers:
    def test_add_member_to_composition(self, client: TestClient, db: Session):
        # Créer des données de test
        owner = UserFactory()
        member = UserFactory()
        role = RoleFactory()
        profession = ProfessionFactory()
        elite_spec = EliteSpecializationFactory(profession=profession)
        composition = CompositionFactory(created_by=owner.id)
        
        db.add_all([owner, member, role, profession, elite_spec, composition])
        db.commit()
        
        token = create_access_token(subject=owner.email)
        
        # Ajouter un membre à la composition
        member_data = {
            "user_id": member.id,
            "role_id": role.id,
            "profession_id": profession.id,
            "elite_specialization_id": elite_spec.id,
            "notes": "Test notes"
        }
        
        response = client.post(
            f"/api/v1/compositions/{composition.id}/members",
            json=member_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Vérifier l'ajout du membre
        db.refresh(composition)
        assert member in composition.members
    
    def test_remove_member_from_composition(self, client: TestClient, db: Session):
        # Créer une composition avec un membre
        owner = UserFactory()
        member = UserFactory()
        composition = CompositionFactory(created_by=owner.id, members=[member])
        db.add_all([owner, member, composition])
        db.commit()
        
        token = create_access_token(subject=owner.email)
        
        # Retirer le membre de la composition
        response = client.delete(
            f"/api/v1/compositions/{composition.id}/members/{member.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Vérifier la suppression du membre
        db.refresh(composition)
        assert member not in composition.members

class TestCompositionPermissions:
    def test_non_owner_cannot_edit_composition(self, client: TestClient, db: Session):
        # Créer un propriétaire et un utilisateur normal
        owner = UserFactory()
        other_user = UserFactory()
        composition = CompositionFactory(created_by=owner.id)
        db.add_all([owner, other_user, composition])
        db.commit()
        
        token = create_access_token(subject=other_user.email)
        
        # Tenter de mettre à jour la composition
        response = client.put(
            f"/api/v1/compositions/{composition.id}",
            json={"name": "Unauthorized Update"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_admin_can_edit_any_composition(self, client: TestClient, db: Session):
        # Créer un admin et une composition appartenant à un autre utilisateur
        admin = UserFactory(is_superuser=True)
        owner = UserFactory()
        composition = CompositionFactory(created_by=owner.id)
        db.add_all([admin, owner, composition])
        db.commit()
        
        token = create_access_token(subject=admin.email)
        
        # L'admin devrait pouvoir mettre à jour la composition
        response = client.put(
            f"/api/v1/compositions/{composition.id}",
            json={"name": "Admin Update"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
