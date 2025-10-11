"""
Tests d'intégration avec l'API Guild Wars 2.

Ce module contient des tests pour vérifier l'intégration avec l'API Guild Wars 2,
y compris la récupération des données de métiers, compétences et caractéristiques.
"""

import pytest
import httpx
from unittest.mock import patch, MagicMock

from app.core.config import settings
from app.services.gw2_api import GW2APIService

# Activer le mode asyncio pour tous les tests
pytestmark = pytest.mark.asyncio

# Données de test simulées
MOCK_PROFESSIONS = {
    "Guardian": {
        "id": "Guardian",
        "name": "Garde",
        "icon": "https://render.guildwars2.com/...",
        "icon_big": "https://render.guildwars2.com/...",
        "specializations": [1, 4, 6],
        "weapons": {"Axe": "Profession", "Sword": "Profession", "Mace": "Profession"},
        "flags": ["NoRacialSkills"],
        "skills": [
            {
                "id": 10185,
                "slot": "Weapon_1",
                "name": "Strike",
                "icon": "https://render.guildwars2.com/...",
                "description": "Slash your foe.",
                "type": "Weapon",
                "weapon_type": "Sword",
                "professions": ["Guardian"],
            }
        ],
    }
}

MOCK_SPECIALIZATIONS = {
    "1": {
        "id": 1,
        "name": "Zeal",
        "profession": "Guardian",
        "elite": False,
        "minor_traits": [632, 633, 634],
        "major_traits": [635, 636, 637, 638, 639, 640, 641, 642, 643],
    }
}

MOCK_TRAITS = {
    "632": {
        "id": 632,
        "name": "Zealous Blade",
        "description": "Gain increased strike damage for each point of burning on your target.",
        "icon": "https://render.guildwars2.com/...",
        "specialization": 1,
        "tier": "Minor",
        "slot": "Minor",
        "facts": [{"type": "Damage", "hit_count": 1, "dmg_multiplier": 0.5}],
    }
}


class TestGW2APIIntegration:
    """Tests d'intégration avec l'API Guild Wars 2."""

    @pytest.fixture
    def mock_httpx_client(self):
        """Crée un client HTTPX mock pour les tests."""
        with patch("httpx.AsyncClient") as mock_client:
            yield mock_client

    @pytest.fixture
    def gw2_service(self, mock_httpx_client):
        """Crée une instance du service GW2API avec un client mock."""
        return GW2APIService()

    async def test_fetch_professions(self, gw2_service, mock_httpx_client):
        """Teste la récupération des métiers depuis l'API GW2."""
        # Configuration du mock
        mock_response = MagicMock()
        mock_response.json.return_value = ["Guardian", "Warrior", "Elementalist"]
        mock_httpx_client.return_value.__aenter__.return_value.get.return_value = mock_response

        # Appel de la méthode à tester
        result = await gw2_service.fetch_professions()

        # Vérifications
        assert isinstance(result, list)
        assert len(result) > 0
        assert "Guardian" in result

        # Vérification que l'URL correcte a été appelée
        mock_httpx_client.return_value.__aenter__.return_value.get.assert_called_once_with(
            f"{settings.GW2_API_BASE_URL}/professions"
        )

    async def test_fetch_profession_details(self, gw2_service, mock_httpx_client):
        """Teste la récupération des détails d'un métier spécifique."""
        # Configuration du mock
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_PROFESSIONS["Guardian"]
        mock_httpx_client.return_value.__aenter__.return_value.get.return_value = mock_response

        # Appel de la méthode à tester
        result = await gw2_service.fetch_profession_details("Guardian")

        # Vérifications
        assert isinstance(result, dict)
        assert result["name"] == "Garde"
        assert "skills" in result
        assert len(result["skills"]) > 0

    async def test_fetch_skills(self, gw2_service, mock_httpx_client):
        """Teste la récupération des compétences."""
        # Configuration du mock
        mock_response = MagicMock()
        mock_response.json.return_value = [10185, 10186, 10187]  # IDs de compétences
        mock_httpx_client.return_value.__aenter__.return_value.get.return_value = mock_response

        # Appel de la méthode à tester
        result = await gw2_service.fetch_skills([10185, 10186, 10187])

        # Vérifications
        assert isinstance(result, list)
        assert len(result) == 3

    async def test_fetch_traits(self, gw2_service, mock_httpx_client):
        """Teste la récupération des caractéristiques."""
        # Configuration du mock
        mock_response = MagicMock()
        mock_response.json.return_value = [632, 633, 634]  # IDs de traits
        mock_httpx_client.return_value.__aenter__.return_value.get.return_value = mock_response

        # Appel de la méthode à tester
        result = await gw2_service.fetch_traits([632, 633, 634])

        # Vérifications
        assert isinstance(result, list)
        assert len(result) == 3

    async def test_sync_professions(self, db, gw2_service, mock_httpx_client):
        """Teste la synchronisation des métiers avec la base de données."""
        # Configuration du mock pour fetch_professions
        mock_professions_response = MagicMock()
        mock_professions_response.json.return_value = ["Guardian", "Warrior"]

        # Configuration du mock pour fetch_profession_details
        mock_details_response = MagicMock()
        mock_details_response.json.side_effect = [
            MOCK_PROFESSIONS["Guardian"],
            MOCK_PROFESSIONS["Guardian"],  # Simuler deux fois le même métier pour le test
        ]

        # Configuration du mock pour les appels HTTP
        mock_httpx_client.return_value.__aenter__.return_value.get.side_effect = [
            mock_professions_response,
            mock_details_response,
            mock_details_response,  # Pour le deuxième appel à fetch_profession_details
        ]

        # Appel de la méthode à tester
        result = await gw2_service.sync_professions()

        # Vérifications
        assert isinstance(result, list)
        assert len(result) == 2  # Deux métiers synchronisés

        # Vérifier que les métiers ont été enregistrés en base de données
        from app.crud.crud_profession import profession as crud_profession

        professions = await crud_profession.get_multi(db)
        assert len(professions) == 2
        assert any(p.name == "Garde" for p in professions)

    async def test_rate_limiting(self, gw2_service, mock_httpx_client):
        """Teste la gestion du rate limiting de l'API GW2."""
        # Configuration du mock pour simuler une réponse 429 (Too Many Requests)
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "5"}
        mock_httpx_client.return_value.__aenter__.return_value.get.return_value = mock_response

        # Configuration du mock pour simuler un succès après un certain temps
        success_response = MagicMock()
        success_response.json.return_value = ["Guardian", "Warrior"]

        # Configurer le mock pour échouer une fois puis réussir
        mock_httpx_client.return_value.__aenter__.return_value.get.side_effect = [mock_response, success_response]

        # Appel de la méthode à tester avec gestion du rate limiting
        result = await gw2_service.fetch_professions()

        # Vérifications
        assert isinstance(result, list)
        assert len(result) == 2

        # Vérifier que le nombre d'appels est correct (2 appels : 1 échec + 1 succès)
        assert mock_httpx_client.return_value.__aenter__.return_value.get.call_count == 2

    async def test_error_handling(self, gw2_service, mock_httpx_client):
        """Teste la gestion des erreurs lors des appels à l'API."""
        # Configuration du mock pour simuler une erreur de connexion
        mock_httpx_client.return_value.__aenter__.return_value.get.side_effect = httpx.RequestError(
            "Erreur de connexion"
        )

        # Appel de la méthode à tester et vérification qu'une exception est levée
        with pytest.raises(httpx.RequestError):
            await gw2_service.fetch_professions()
