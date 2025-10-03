"""
Tests d'API pour les endpoints liés aux builds.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import User, Build, Profession


@pytest.mark.api
class TestBuildsAPI:
    """Tests pour les endpoints d'API des builds."""

    async def test_read_builds(self, async_client: AsyncClient, auth_headers, build_factory, user_factory, db: AsyncSession):
        """Teste que la liste des builds ne contient que les builds publics et ceux de l'utilisateur."""
        user_headers = await auth_headers(username="testuser", password="password")
        user = await user_crud.get_by_username_async(db, username="testuser")
        another_user = await user_factory(username="anotheruser", email="another@user.com", password="password")
        
        public_build = await build_factory(name="Public Build", is_public=True, user=another_user)
        private_build_other_user = await build_factory(name="Private Build", is_public=False, user=another_user)
        private_build_current_user = await build_factory(name="My Private Build", is_public=False, user=user)

        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/", headers=user_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # L'utilisateur devrait voir le build public et son propre build privé.
        assert len(data) == 2
        build_names = {b['name'] for b in data}
        assert public_build.name in build_names
        assert private_build_current_user.name in build_names
        assert private_build_other_user.name not in build_names

    async def test_read_build(self, async_client: AsyncClient, auth_headers, build_factory):
        """Teste la récupération d'un build par son ID."""
        headers = await auth_headers()
        build = await build_factory(name="Readable Build", is_public=True)

        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/{build.id}",
            headers=headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == build.id
        assert data["name"] == build.name

    async def test_read_private_build_unauthorized(
        self, async_client: AsyncClient, auth_headers, build_factory, user_factory
    ):
        """Teste qu'un utilisateur ne peut pas accéder à un build privé qui ne lui appartient pas."""
        owner = await user_factory(username="owner", password="password")
        private_build = await build_factory(name="Private Build", is_public=False, user=owner)
        
        # A different user tries to access it
        other_user_headers = await auth_headers(username="other", password="password")

        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/{private_build.id}",
            headers=other_user_headers,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "detail" in response.json()
        assert "Not enough permissions" in response.json()["detail"]

    async def test_full_build_lifecycle(
        self, async_client: AsyncClient, auth_headers, profession_factory
    ):
        """Teste un cycle de vie complet : création, lecture, mise à jour et suppression."""
        user_headers = await auth_headers(username="lifecycle_user", password="password")
        profession = await profession_factory()

        # 1. Création
        create_data = {
            "name": "Lifecycle Build",
            "game_mode": "wvw",
            "profession_ids": [profession.id],
        }
        create_response = await async_client.post(f"{settings.API_V1_STR}/builds/", json=create_data, headers=user_headers)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_data = create_response.json()
        build_id = created_data["id"]
        assert created_data["name"] == "Lifecycle Build"
        assert created_data["game_mode"] == "wvw"
        assert created_data["is_public"] is True # Default value
        # Vérifier que la profession est bien associée au build créé
        profession_ids = {p["id"] for p in created_data.get("professions", [])}
        assert profession.id in profession_ids

        # 2. Lecture (détail)
        get_response = await async_client.get(f"{settings.API_V1_STR}/builds/{build_id}", headers=user_headers)
        assert get_response.status_code == status.HTTP_200_OK
        read_data = get_response.json()
        assert read_data["id"] == build_id
        assert read_data["name"] == "Lifecycle Build"

        # 3. Mise à jour
        update_data = {"name": "Updated Lifecycle Build", "is_public": False}
        update_response = await async_client.put(f"{settings.API_V1_STR}/builds/{build_id}", json=update_data, headers=user_headers)
        assert update_response.status_code == status.HTTP_200_OK
        updated_data = update_response.json()
        assert updated_data["name"] == "Updated Lifecycle Build"
        assert updated_data["is_public"] is False

        # 4. Suppression
        delete_response = await async_client.delete(f"{settings.API_V1_STR}/builds/{build_id}", headers=user_headers)
        assert delete_response.status_code == status.HTTP_200_OK
        assert delete_response.json()["id"] == build_id

        # 5. Vérification de la suppression
        final_get_response = await async_client.get(f"{settings.API_V1_STR}/builds/{build_id}", headers=user_headers)
        assert final_get_response.status_code == status.HTTP_404_NOT_FOUND

    async def test_create_build(
        self, async_client: AsyncClient, db: AsyncSession, auth_headers, profession_factory
    ):
        """Teste la création d'un nouveau build et vérifie son propriétaire."""
        # Crée un utilisateur et obtient ses headers d'authentification
        user_headers = await auth_headers(username="creator", password="password")
        profession = await profession_factory()

        build_data = {
            "name": "New API Test Build",
            "description": "A test build created via API",
            "game_mode": "wvw",
            "is_public": True,
            "profession_ids": [profession.id],
        }
        
        # L'utilisateur "creator" est implicitement créé par auth_headers
        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json=build_data,
            headers=user_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert "id" in data
        assert data["name"] == "New API Test Build"
        assert data["is_public"] is True
        assert data["profession_ids"] == [profession.id]
        
        # Vérification explicite en base de données
        from app.crud import user_crud
        user = await user_crud.get_by_username_async(db, username="creator")
        assert user is not None
        assert data["created_by_id"] == user.id

    async def test_create_build_with_multiple_professions(
        self, async_client: AsyncClient, db: AsyncSession, auth_headers, profession_factory
    ):
        """Teste la création d'un build avec plusieurs professions et vérifie les associations."""
        user_headers = await auth_headers(username="multi_prof_user", password="password")
        prof1 = await profession_factory(name="Profession A")
        prof2 = await profession_factory(name="Profession B")

        build_data = {
            "name": "Multi-Profession Build",
            "game_mode": "wvw",
            "profession_ids": [prof1.id, prof2.id],
        }

        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json=build_data,
            headers=user_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        build_id = data["id"]

        # Vérification en base de données
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        stmt = select(Build).options(selectinload(Build.professions)).where(Build.id == build_id)
        result = await db.execute(stmt)
        db_build = result.scalar_one()
        
        assert len(db_build.professions) == 2
        assert {p.id for p in db_build.professions} == {prof1.id, prof2.id}

    async def test_update_build(
        self, async_client: AsyncClient, auth_headers, build_factory, user_factory
    ):
        """Teste la mise à jour d'un build existant."""
        user = await user_factory(username="owner", password="password")
        headers = await auth_headers(username="owner", password="password")
        user_build = await build_factory(user=user)

        update_data = {
            "name": "Updated Build Name",
            "description": "Updated description via API",
            "is_public": False,
        }

        response = await async_client.put(
            f"{settings.API_V1_STR}/builds/{user_build.id}",
            json=update_data,
            headers=headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["name"] == "Updated Build Name"
        assert data["description"] == "Updated description via API"
        assert data["is_public"] is False

    async def test_update_build_professions(
        self, async_client: AsyncClient, db: AsyncSession, auth_headers, build_factory, profession_factory, user_factory
    ):
        """Teste la mise à jour des professions associées à un build."""
        # 1. Créer un utilisateur, des professions et un build initial
        user = await user_factory(username="update_prof_user", password="password")
        headers = await auth_headers(username="update_prof_user", password="password")
        
        prof1 = await profession_factory(name="Initial Prof 1")
        prof2 = await profession_factory(name="Initial Prof 2")
        prof3 = await profession_factory(name="New Prof 3")

        user_build = await build_factory(user=user, professions=[prof1])

        # 2. Préparer les données de mise à jour pour changer les professions
        update_data = {
            "name": user_build.name, # Le nom ne change pas
            "profession_ids": [prof2.id, prof3.id] # Remplacer prof1 par prof2 et prof3
        }

        # 3. Envoyer la requête de mise à jour
        response = await async_client.put(
            f"{settings.API_V1_STR}/builds/{user_build.id}",
            json=update_data,
            headers=headers,
        )

        # 4. Vérifier la réponse et l'état de la base de données
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["professions"]) == 2
        
        await db.refresh(user_build, attribute_names=["professions"])
        
        final_prof_ids = {p.id for p in user_build.professions}
        assert final_prof_ids == {prof2.id, prof3.id}

    async def test_update_other_users_build(
        self, async_client: AsyncClient, auth_headers, build_factory, user_factory
    ):
        """Teste qu'un utilisateur ne peut pas mettre à jour un build qui ne lui appartient pas."""
        owner = await user_factory(username="owner", password="password")
        other_user_build = await build_factory(user=owner)

        other_user_headers = await auth_headers(username="other", password="password")

        response = await async_client.put(
            f"{settings.API_V1_STR}/builds/{other_user_build.id}",
            json={"name": "Unauthorized Update"},
            headers=other_user_headers,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "detail" in response.json()
        assert "Not enough permissions" in response.json()["detail"]

    async def test_delete_build(
        self, async_client: AsyncClient, auth_headers, build_factory, user_factory
    ):
        """Teste la suppression d'un build."""
        user = await user_factory(username="owner", password="password")
        headers = await auth_headers(username="owner", password="password")
        build_to_delete = await build_factory(user=user)

        delete_response = await async_client.delete(
            f"{settings.API_V1_STR}/builds/{build_to_delete.id}", headers=headers
        )

        assert delete_response.status_code == status.HTTP_200_OK
        data = delete_response.json()
        assert data["id"] == build_to_delete.id

        get_response = await async_client.get(
            f"{settings.API_V1_STR}/builds/{build_to_delete.id}", headers=headers
        )

        assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.api
class TestBuildsAPIEdgeCases:
    """Tests pour les cas limites et les erreurs des endpoints de builds."""

    async def test_create_build_unauthenticated(self, async_client: AsyncClient):
        """Teste que la création d'un build sans authentification échoue."""
        invalid_build_data = {
            "name": "Unauthorized Build",
            "description": "This should fail",
            "game_mode": "wvw",
            "is_public": True,
            "profession_ids": [1],
        }
        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/", json=invalid_build_data
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_build_with_invalid_data(self, async_client: AsyncClient, auth_headers):
        """Teste la création d'un build avec des données invalides (erreur de validation)."""
        headers = await auth_headers()
        
        # Données invalides : nom trop court
        invalid_build_data = {
            "name": "a",
            "description": "A test build",
            "game_mode": "wvw",
            "is_public": True,
            "profession_ids": [1],
        }

        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json=invalid_build_data,
            headers=headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["detail"]
        assert any("at least 3 characters" in err["msg"] for err in errors if err["loc"] == ["body", "name"])

    async def test_create_build_with_name_too_long(self, async_client: AsyncClient, auth_headers):
        """Teste la création d'un build avec un nom trop long."""
        headers = await auth_headers()
        
        invalid_build_data = {
            "name": "a" * 101,  # max_length is 100
            "description": "A test build",
            "game_mode": "wvw",
            "is_public": True,
            "profession_ids": [1],
        }

        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json=invalid_build_data,
            headers=headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["detail"]
        assert any("at most 100 characters" in err["msg"] for err in errors if err["loc"] == ["body", "name"])

    async def test_create_build_with_empty_professions(self, async_client: AsyncClient, auth_headers):
        """Teste la création d'un build avec une liste de professions vide."""
        headers = await auth_headers()
        build_data = {
            "name": "Build with no professions",
            "game_mode": "pve",
            "profession_ids": [],  # Liste vide, ce qui est invalide (min_length=1)
        }

        response = await async_client.post(f"{settings.API_V1_STR}/builds/", json=build_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["detail"]
        assert any("at least 1 item" in err["msg"] for err in errors if err["loc"] == ["body", "profession_ids"])

    async def test_create_build_with_too_many_professions(self, async_client: AsyncClient, auth_headers, profession_factory):
        """Teste la création d'un build avec trop de professions (max_length=3)."""
        headers = await auth_headers()
        prof1 = await profession_factory(name="p1")
        prof2 = await profession_factory(name="p2")
        prof3 = await profession_factory(name="p3")
        prof4 = await profession_factory(name="p4")
        
        build_data = {
            "name": "Build with too many professions",
            "game_mode": "pve",
            "profession_ids": [prof1.id, prof2.id, prof3.id, prof4.id],
        }

        response = await async_client.post(f"{settings.API_V1_STR}/builds/", json=build_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["detail"]
        assert any("at most 3 items" in err["msg"] for err in errors if err["loc"] == ["body", "profession_ids"])

    async def test_create_build_with_invalid_game_mode(self, async_client: AsyncClient, auth_headers):
        """Teste la création d'un build avec un game_mode invalide."""
        headers = await auth_headers()
        build_data = {
            "name": "Invalid Game Mode Build",
            "game_mode": "invalid_mode",
            "profession_ids": [1],
        }
        response = await async_client.post(f"{settings.API_V1_STR}/builds/", json=build_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["detail"]
        assert any("Input should be 'wvw', 'pvp', 'pve', 'raids' or 'fractals'" in err["msg"] for err in errors if err["loc"] == ["body", "game_mode"])

    @pytest.mark.parametrize("size", [0, 51])
    async def test_create_build_with_invalid_team_size(self, async_client: AsyncClient, auth_headers, size):
        """Teste la création d'un build avec une team_size invalide."""
        headers = await auth_headers()
        build_data = {
            "name": "Invalid Team Size Build",
            "game_mode": "wvw",
            "team_size": size,
            "profession_ids": [1],
        }
        response = await async_client.post(f"{settings.API_V1_STR}/builds/", json=build_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["detail"]
        if size < 1:
            assert any("greater than or equal to 1" in err["msg"] for err in errors if err["loc"] == ["body", "team_size"])
        else:
            assert any("less than or equal to 50" in err["msg"] for err in errors if err["loc"] == ["body", "team_size"])

    async def test_create_build_with_nonexistent_profession(self, async_client: AsyncClient, auth_headers):
        """Teste la création d'un build avec un ID de profession qui n'existe pas."""
        headers = await auth_headers()
        build_data = {
            "name": "Build with invalid profession",
            "game_mode": "pve",
            "profession_ids": [99999],  # ID qui n'existe pas
        }

        response = await async_client.post(f"{settings.API_V1_STR}/builds/", json=build_data, headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    async def test_create_build_with_forbidden_professions(self, async_client: AsyncClient, auth_headers, profession_factory):
        """Teste la création d'un build avec une combinaison de professions interdite."""
        headers = await auth_headers()
        # Simuler des professions avec des IDs qui correspondent à une règle métier
        # Notre validateur interdit la combinaison {1, 2}
        prof1 = await profession_factory(id=1, name="Guardian")
        prof2 = await profession_factory(id=2, name="Firebrand")

        build_data = {
            "name": "Forbidden Combo Build",
            "game_mode": "pve",
            "profession_ids": [prof1.id, prof2.id],
        }

        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/", json=build_data, headers=headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["detail"]
        assert any(
            "cannot be used together" in err["msg"] for err in errors if err["loc"] == ["body", "profession_ids"]
        )

    async def test_delete_other_users_build(
        self, async_client: AsyncClient, auth_headers, profession_factory
    ):
        """Test creating a build with duplicate profession IDs."""
        headers = await auth_headers()
        profession = await profession_factory()
        build_data = {
            "name": "Test Build Duplicate Profs",
            "description": "Test with duplicate professions",
            "profession_ids": [profession.id, profession.id],  # Duplicate IDs
            "game_mode": "pve",
        }

        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/", json=build_data, headers=headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "Profession IDs must be unique" in response.text

    async def test_delete_other_users_build(
        self, async_client: AsyncClient, auth_headers, profession_factory
    ):
        """Test creating a build with duplicate profession IDs."""
        headers = await auth_headers()
        profession = await profession_factory()
        build_data = {
            "name": "Test Build Duplicate Profs",
            "description": "Test with duplicate professions",
            "profession_ids": [profession.id, profession.id],  # Duplicate IDs
            "game_mode": "pve",
        }

        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/", json=build_data, headers=headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "Profession IDs must be unique" in response.text

    async def test_delete_other_users_build(
        self, async_client: AsyncClient, auth_headers, build_factory, user_factory
    ):
        """Teste qu'un utilisateur ne peut pas supprimer un build qui ne lui appartient pas."""
        owner = await user_factory(username="owner", password="password")
        other_user_build = await build_factory(user=owner)

        other_user_headers = await auth_headers(username="other", password="password")

        response = await async_client.delete(
            f"{settings.API_V1_STR}/builds/{other_user_build.id}",
            headers=other_user_headers,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "detail" in response.json()
        assert "Not enough permissions" in response.json()["detail"]


    async def test_update_build_to_forbidden_combination(
        self, async_client: AsyncClient, auth_headers, build_factory, profession_factory, user_factory
    ):
        """Teste la mise à jour d'un build vers une combinaison de professions interdite."""
        # 1. Créer un utilisateur et des professions initiales valides
        user = await user_factory(username="update_forbidden_user", password="password")
        headers = await auth_headers(username="update_forbidden_user", password="password")
        
        # Professions initiales (non interdites)
        prof_valid_1 = await profession_factory(id=3, name="Valid Prof 1")
        prof_valid_2 = await profession_factory(id=4, name="Valid Prof 2")
        
        # Créer un build avec ces professions valides
        user_build = await build_factory(user=user, professions=[prof_valid_1, prof_valid_2])

        # 2. Préparer les professions qui forment une combinaison interdite
        # La règle est {1, 2} est interdite
        prof_forbidden_1 = await profession_factory(id=1, name="Guardian")
        prof_forbidden_2 = await profession_factory(id=2, name="Firebrand")

        # 3. Tenter de mettre à jour le build avec la combinaison interdite
        update_data = {
            "name": user_build.name, # Le nom ne change pas
            "profession_ids": [prof_forbidden_1.id, prof_forbidden_2.id]
        }

        response = await async_client.put(
            f"{settings.API_V1_STR}/builds/{user_build.id}",
            json=update_data,
            headers=headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["detail"]
        assert any(
            "cannot be used together" in err["msg"] for err in errors if err["loc"] == ["body", "profession_ids"]
        )

@pytest.mark.api
class TestBuildsAPIPermissions:
    """Tests pour les permissions des endpoints de builds."""

    async def test_unauthenticated_access(self, async_client: AsyncClient, build_factory):
        """Teste que les endpoints protégés nécessitent une authentification."""
        public_build = await build_factory(is_public=True)

        endpoints = [
            ("GET", f"{settings.API_V1_STR}/builds/"),
            ("GET", f"{settings.API_V1_STR}/builds/{public_build.id}"),
            ("POST", f"{settings.API_V1_STR}/builds/"),
            ("PUT", f"{settings.API_V1_STR}/builds/{public_build.id}"),
            ("DELETE", f"{settings.API_V1_STR}/builds/{public_build.id}"),
        ]

        for method, url in endpoints:
            if method == "GET":
                response = await async_client.get(url)
            elif method == "POST":
                response = await async_client.post(url, json={})
            elif method == "PUT":
                response = await async_client.put(url, json={})
            elif method == "DELETE":
                response = await async_client.delete(url)

            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_admin_access(
        self, async_client: AsyncClient, auth_headers, build_factory, user_factory
    ):
        """Teste qu'un administrateur peut accéder à tous les builds."""
        owner = await user_factory(username="owner", password="password")
        private_build = await build_factory(user=owner, is_public=False)

        admin_headers = await auth_headers(username="admin", password="password", is_superuser=True)

        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/{private_build.id}",
            headers=admin_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == private_build.id

    async def test_admin_can_delete_any_build(
        self, async_client: AsyncClient, auth_headers, build_factory, user_factory
    ):
        """Teste qu'un administrateur peut supprimer n'importe quel build."""
        owner = await user_factory(username="owner", password="password")
        build_to_delete = await build_factory(user=owner)

        admin_headers = await auth_headers(username="admin", password="password", is_superuser=True)

        delete_response = await async_client.delete(
            f"{settings.API_V1_STR}/builds/{build_to_delete.id}", headers=admin_headers
        )

        assert delete_response.status_code == status.HTTP_200_OK
        assert delete_response.json()["id"] == build_to_delete.id

        get_response = await async_client.get(
            f"{settings.API_V1_STR}/builds/{build_to_delete.id}", headers=admin_headers
        )

        assert get_response.status_code == status.HTTP_404_NOT_FOUND
