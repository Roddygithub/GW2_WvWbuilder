"""
Tests d'API pour les endpoints liés aux builds.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.core.config import settings


@pytest.mark.api
class TestBuildsAPI:
    """Tests pour les endpoints d'API des builds."""

    def test_read_builds(self, client: TestClient, auth_headers: dict):
        """Teste la récupération de la liste des builds."""
        # Récupérer les builds publics
        response = client.get(
            f"{settings.API_V1_STR}/builds/", headers=auth_headers["user"]
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

        # Vérifier que seuls les builds publics sont renvoyés
        for build in data:
            assert build["is_public"] is True

    def test_read_build(self, client: TestClient, test_data: dict, auth_headers: dict):
        """Teste la récupération d'un build par son ID."""
        # Récupérer un build public existant
        public_build = next(
            build for build in test_data["builds"].values() if build.is_public
        )

        # Tester la récupération du build
        response = client.get(
            f"{settings.API_V1_STR}/builds/{public_build.id}",
            headers=auth_headers["user"],
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(public_build.id)
        assert data["name"] == public_build.name

    def test_read_private_build_unauthorized(
        self, client: TestClient, test_data: dict, auth_headers: dict
    ):
        """Teste qu'un utilisateur ne peut pas accéder à un build privé qui ne lui appartient pas."""
        # Récupérer un build privé existant
        private_build = next(
            build for build in test_data["builds"].values() if not build.is_public
        )

        # Tester l'accès non autorisé au build privé
        response = client.get(
            f"{settings.API_V1_STR}/builds/{private_build.id}",
            headers=auth_headers["user"],
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "detail" in response.json()
        assert "Not enough permissions" in response.json()["detail"]

    def test_create_build(
        self, client: TestClient, test_data: dict, auth_headers: dict
    ):
        """Teste la création d'un nouveau build."""
        # Récupérer des données de test
        profession = test_data["professions"]["warrior"]
        elite_spec = test_data["elite_specs"]["berserker"]

        # Données pour la création du build
        build_data = {
            "name": "New API Test Build",
            "description": "A test build created via API",
            "is_public": True,
            "profession_id": str(profession.id),
            "elite_spec_id": str(elite_spec.id),
            "weapons": ["Axe", "Axe"],
            "skills": ["Banner of Strength", "Banner of Discipline"],
            "traits": {
                "Strength": [1, 2, 1],
                "Discipline": [2, 2, 1],
                "Berserker": [1, 2, 3],
            },
            "equipment": {
                "weapons": ["Axe", "Axe"],
                "armor": ["Berserker's"],
                "trinkets": ["Berserker's"],
            },
            "infusions": {
                "weapons": ["+9 Agony Infusion"],
                "armor": [],
                "trinkets": [],
            },
            "consumables": {
                "food": "Bowl of Sweet and Spicy Butternut Squash Soup",
                "utility": "Superior Sharpening Stone",
            },
            "attributes": {
                "power": 3000,
                "precision": 2000,
                "ferocity": 1500,
                "vitality": 1000,
            },
            "skills_guide": "Start with banner and burst rotation...",
            "rotation_guide": "Maintain might stacks and use banners on cooldown...",
            "video_guide_url": "https://example.com/build-video",
            "gw2skills_url": "https://lucky-noobs.com/builds/view/12345",
        }

        # Créer le build
        response = client.post(
            f"{settings.API_V1_STR}/builds/",
            json=build_data,
            headers=auth_headers["user"],
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Vérifier les données renvoyées
        assert "id" in data
        assert data["name"] == "New API Test Build"
        assert data["is_public"] is True
        assert data["profession_id"] == str(profession.id)
        assert data["elite_spec_id"] == str(elite_spec.id)
        assert data["weapons"] == ["Axe", "Axe"]
        assert len(data["skills"]) == 2
        assert "Banner of Strength" in data["skills"]

    def test_update_build(
        self, client: TestClient, test_data: dict, auth_headers: dict
    ):
        """Teste la mise à jour d'un build existant."""
        # Récupérer un build appartenant à l'utilisateur
        user = test_data["users"]["user"]
        user_build = next(
            build for build in test_data["builds"].values() if build.user_id == user.id
        )

        # Données de mise à jour
        update_data = {
            "name": "Updated Build Name",
            "description": "Updated description via API",
            "is_public": False,
            "weapons": ["Greatsword", "Axe/Axe"],
            "skills": ["Banner of Strength", "Banner of Discipline", "Signet of Might"],
        }

        # Mettre à jour le build
        response = client.put(
            f"{settings.API_V1_STR}/builds/{user_build.id}",
            json=update_data,
            headers=auth_headers["user"],
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Vérifier les données mises à jour
        assert data["name"] == "Updated Build Name"
        assert data["description"] == "Updated description via API"
        assert data["is_public"] is False
        assert "Greatsword" in data["weapons"]
        assert len(data["skills"]) == 3
        assert "Signet of Might" in data["skills"]

    def test_update_other_users_build(
        self, client: TestClient, test_data: dict, auth_headers: dict
    ):
        """Teste qu'un utilisateur ne peut pas mettre à jour un build qui ne lui appartient pas."""
        # Récupérer un build qui n'appartient pas à l'utilisateur
        other_user_build = next(
            build
            for build in test_data["builds"].values()
            if build.user_id != test_data["users"]["user"].id
        )

        # Tenter de mettre à jour le build
        response = client.put(
            f"{settings.API_V1_STR}/builds/{other_user_build.id}",
            json={"name": "Unauthorized Update"},
            headers=auth_headers["user"],
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "detail" in response.json()
        assert "Not enough permissions" in response.json()["detail"]

    def test_delete_build(
        self, client: TestClient, test_data: dict, auth_headers: dict, db
    ):
        """Teste la suppression d'un build."""
        # Créer un nouveau build pour le test
        test_data["users"]["user"]
        profession = test_data["professions"]["warrior"]
        elite_spec = test_data["elite_specs"]["berserker"]

        build_data = {
            "name": "Build to Delete",
            "description": "This build will be deleted",
            "is_public": True,
            "profession_id": str(profession.id),
            "elite_spec_id": str(elite_spec.id),
            "weapons": ["Axe", "Axe"],
            "skills": [],
            "traits": {},
        }

        # Créer le build
        create_response = client.post(
            f"{settings.API_V1_STR}/builds/",
            json=build_data,
            headers=auth_headers["user"],
        )

        build_id = create_response.json()["id"]

        # Supprimer le build
        delete_response = client.delete(
            f"{settings.API_V1_STR}/builds/{build_id}", headers=auth_headers["user"]
        )

        assert delete_response.status_code == status.HTTP_200_OK
        data = delete_response.json()
        assert data["id"] == build_id

        # Vérifier que le build a bien été supprimé
        get_response = client.get(
            f"{settings.API_V1_STR}/builds/{build_id}", headers=auth_headers["user"]
        )

        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_other_users_build(
        self, client: TestClient, test_data: dict, auth_headers: dict
    ):
        """Teste qu'un utilisateur ne peut pas supprimer un build qui ne lui appartient pas."""
        # Récupérer un build qui n'appartient pas à l'utilisateur
        other_user_build = next(
            build
            for build in test_data["builds"].values()
            if build.user_id != test_data["users"]["user"].id
        )

        # Tenter de supprimer le build
        response = client.delete(
            f"{settings.API_V1_STR}/builds/{other_user_build.id}",
            headers=auth_headers["user"],
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "detail" in response.json()
        assert "Not enough permissions" in response.json()["detail"]

    def test_search_builds(
        self, client: TestClient, test_data: dict, auth_headers: dict
    ):
        """Teste la recherche de builds."""
        # Rechercher des builds avec un terme spécifique
        search_term = "Berserker"
        response = client.get(
            f"{settings.API_V1_STR}/builds/search/",
            params={"q": search_term, "skip": 0, "limit": 10},
            headers=auth_headers["user"],
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

        # Vérifier que les résultats contiennent le terme de recherche
        for build in data:
            assert (search_term.lower() in build["name"].lower()) or (
                build["description"]
                and search_term.lower() in build["description"].lower()
            )

    def test_get_user_builds(
        self, client: TestClient, test_data: dict, auth_headers: dict
    ):
        """Teste la récupération des builds d'un utilisateur spécifique."""
        # Récupérer un utilisateur de test
        user = test_data["users"]["user"]

        # Récupérer les builds de l'utilisateur
        response = client.get(
            f"{settings.API_V1_STR}/users/{user.id}/builds",
            headers=auth_headers["user"],
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

        # Vérifier que seuls les builds de l'utilisateur sont renvoyés
        for build in data:
            assert build["user_id"] == str(user.id)

    def test_get_other_user_builds(
        self, client: TestClient, test_data: dict, auth_headers: dict
    ):
        """Teste qu'un utilisateur ne peut voir que les builds publics des autres utilisateurs."""
        # Récupérer un autre utilisateur
        other_user = test_data["users"]["admin"]

        # Récupérer les builds de l'autre utilisateur
        response = client.get(
            f"{settings.API_V1_STR}/users/{other_user.id}/builds",
            headers=auth_headers["user"],
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Vérifier que seuls les builds publics sont renvoyés
        for build in data:
            assert build["is_public"] is True
            assert build["user_id"] == str(other_user.id)


@pytest.mark.api
class TestBuildsAPIPermissions:
    """Tests pour les permissions des endpoints de builds."""

    def test_unauthenticated_access(self, client: TestClient, test_data: dict):
        """Teste que les endpoints protégés nécessitent une authentification."""
        # Récupérer un build public existant
        public_build = next(
            build for build in test_data["builds"].values() if build.is_public
        )

        # Tester l'accès non authentifié à différents endpoints
        endpoints = [
            ("GET", f"{settings.API_V1_STR}/builds/"),
            ("GET", f"{settings.API_V1_STR}/builds/{public_build.id}"),
            ("POST", f"{settings.API_V1_STR}/builds/"),
            ("PUT", f"{settings.API_V1_STR}/builds/{public_build.id}"),
            ("DELETE", f"{settings.API_V1_STR}/builds/{public_build.id}"),
            ("GET", f"{settings.API_V1_STR}/builds/search/"),
            ("GET", f"{settings.API_V1_STR}/users/{public_build.user_id}/builds"),
        ]

        for method, url in endpoints:
            if method == "GET":
                response = client.get(url)
            elif method == "POST":
                response = client.post(url, json={})
            elif method == "PUT":
                response = client.put(url, json={})
            elif method == "DELETE":
                response = client.delete(url)

            # Les endpoints GET peuvent être accessibles sans authentification
            if method == "GET":
                assert response.status_code != status.HTTP_401_UNAUTHORIZED
            else:
                assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_admin_access(
        self, client: TestClient, test_data: dict, auth_headers: dict
    ):
        """Teste qu'un administrateur peut accéder à tous les builds."""
        # Récupérer un build privé
        private_build = next(
            build for build in test_data["builds"].values() if not build.is_public
        )

        # L'administrateur devrait pouvoir accéder au build privé
        response = client.get(
            f"{settings.API_V1_STR}/builds/{private_build.id}",
            headers=auth_headers["admin"],
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == str(private_build.id)

    def test_admin_can_delete_any_build(
        self, client: TestClient, test_data: dict, auth_headers: dict, db
    ):
        """Teste qu'un administrateur peut supprimer n'importe quel build."""
        # Créer un nouveau build avec un utilisateur non administrateur
        test_data["users"]["user"]
        profession = test_data["professions"]["warrior"]
        elite_spec = test_data["elite_specs"]["berserker"]

        build_data = {
            "name": "Build for Admin Deletion Test",
            "description": "This build will be deleted by admin",
            "is_public": True,
            "profession_id": str(profession.id),
            "elite_spec_id": str(elite_spec.id),
            "weapons": ["Axe", "Axe"],
            "skills": [],
            "traits": {},
        }

        # Créer le build avec l'utilisateur non administrateur
        create_response = client.post(
            f"{settings.API_V1_STR}/builds/",
            json=build_data,
            headers=auth_headers["user"],
        )

        build_id = create_response.json()["id"]

        # L'administrateur devrait pouvoir supprimer le build
        delete_response = client.delete(
            f"{settings.API_V1_STR}/builds/{build_id}", headers=auth_headers["admin"]
        )

        assert delete_response.status_code == status.HTTP_200_OK
        assert delete_response.json()["id"] == build_id

        # Vérifier que le build a bien été supprimé
        get_response = client.get(
            f"{settings.API_V1_STR}/builds/{build_id}", headers=auth_headers["admin"]
        )

        assert get_response.status_code == status.HTTP_404_NOT_FOUND
