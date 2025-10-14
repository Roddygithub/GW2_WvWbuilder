"""
Tests for the Guild Wars 2 API client.

These tests verify the functionality of the GW2Client class,
including request handling, error management, and response parsing.
"""

from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.core.gw2.client import GW2Client
from app.core.gw2.exceptions import (
    GW2APINotFoundError,
    GW2APIUnauthorizedError,
)
from app.core.gw2 import models
from app.main import app

# Test data
TEST_ACCOUNT = {
    "id": "test-account-id",
    "name": "Test Account",
    "age": 12345,
    "world": 1001,
    "guilds": ["guild1", "guild2"],
    "guild_leader": ["guild1"],
    "created": "2012-08-28T19:24:12.000Z",
    "access": ["GuildWars2", "HeartOfThorns", "PathOfFire"],
    "commander": True,
    "fractal_level": 100,
    "daily_ap": 15000,
    "monthly_ap": 1000,
    "wvw_rank": 500,
    "last_modified": "2023-01-01T00:00:00.000Z",
}

TEST_CHARACTER = {
    "name": "Test Character",
    "race": "Human",
    "gender": "Female",
    "profession": "Elementalist",
    "level": 80,
    "guild": "guild1",
    "age": 86400,
    "created": "2022-01-01T00:00:00.000Z",
    "deaths": 5,
    "title": 1,
    "equipment": [{"id": 12345, "slot": "Coat", "binding": "Account"}],
    "equipment_pvp": {},
    "specializations": {
        "pve": [{"id": 1, "traits": [1, 2, 3]}, {"id": 2, "traits": [4, 5, 6]}, {"id": 3, "traits": [7, 8, 9]}]
    },
    "skills": {
        "pve": [
            {"id": 1, "slot": "Heal"},
            {"id": 2, "slot": "Utility"},
            {"id": 3, "slot": "Utility"},
            {"id": 4, "slot": "Utility"},
            {"id": 5, "slot": "Elite"},
        ]
    },
    "equipment_tabs": [],
    "build_tabs": [],
    "active_equipment_tab": 0,
    "active_build_tab": 0,
}

TEST_ITEM = {
    "id": 12345,
    "name": "Test Item",
    "type": "Weapon",
    "level": 80,
    "rarity": "Exotic",
    "vendor_value": 1000,
    "default_skin": 67890,
    "icon": "https://render.guildwars2.com/...",
    "flags": ["SoulBindOnUse"],
    "game_types": ["Activity", "Dungeon", "Pve"],
    "restrictions": [],
}

TEST_PROFESSION = {
    "id": "Elementalist",
    "name": "Elementalist",
    "icon": "https://render.guildwars2.com/...",
    "icon_big": "https://render.guildwars2.com/.../big",
    "specializations": [1, 2, 3],
    "weapons": {
        "Axe": ["Mainhand"],
        "Dagger": ["Mainhand", "Offhand"],
        "Focus": ["Offhand"],
        "Scepter": ["Mainhand"],
        "Staff": ["TwoHand"],
        "Sword": ["Mainhand"],
        "Warhorn": ["Offhand"],
    },
    "training": [],
    "flags": ["NoRacialSkills"],
}


@pytest.fixture
def gw2_client():
    """Fixture to provide a GW2Client instance for testing."""
    with patch("aiohttp.ClientSession") as mock_session:
        client = GW2Client(api_key="test_api_key")
        client.session = mock_session.return_value
        client.session.get = AsyncMock()
        client.session.post = AsyncMock()
        yield client


@pytest.fixture
def mock_response():
    """Fixture to create a mock response with JSON data."""

    def _create_mock_response(status_code=200, json_data=None, headers=None):
        mock = AsyncMock()
        mock.status = status_code
        mock.json.return_value = json_data or {}
        mock.headers = headers or {}
        return mock

    return _create_mock_response


class TestGW2Client:
    """Test suite for the GW2Client class."""

    @pytest.mark.asyncio
    async def test_get_account_success(self, gw2_client, mock_response):
        """Test successful account retrieval."""
        # Setup mock response
        gw2_client.session.get.return_value.__aenter__.return_value = mock_response(
            status_code=200,
            json_data=TEST_ACCOUNT,
            headers={"X-Rate-Limit-Limit": "600", "X-Rate-Limit-Remaining": "599"},
        )

        # Call the method
        account = await gw2_client.get_account()

        # Verify the result
        assert account.id == "test-account-id"
        assert account.name == "Test Account"
        assert account.world == 1001
        assert len(account.guilds) == 2
        assert "GuildWars2" in account.access
        assert account.commander is True

        # Verify the request was made correctly
        gw2_client.session.get.assert_called_once()
        args, kwargs = gw2_client.session.get.call_args
        assert "account" in args[0]
        assert kwargs["headers"]["Authorization"] == "Bearer test_api_key"

    @pytest.mark.asyncio
    async def test_get_character_success(self, gw2_client, mock_response):
        """Test successful character retrieval."""
        gw2_client.session.get.return_value.__aenter__.return_value = mock_response(
            status_code=200, json_data=TEST_CHARACTER
        )

        character = await gw2_client.get_character("Test Character")

        assert character.name == "Test Character"
        assert character.race == "Human"
        assert character.profession == "Elementalist"
        assert character.level == 80
        assert len(character.specializations["pve"]) == 3

    @pytest.mark.asyncio
    async def test_get_character_not_found(self, gw2_client, mock_response):
        """Test handling of character not found error."""
        gw2_client.session.get.return_value.__aenter__.return_value = mock_response(
            status_code=404, json_data={"text": "no such id"}
        )

        with pytest.raises(GW2APINotFoundError):
            await gw2_client.get_character("NonexistentCharacter")

    @pytest.mark.asyncio
    async def test_rate_limiting(self, gw2_client, mock_response):
        """Test rate limit handling with retry logic."""
        # First response: rate limit exceeded
        rate_limit_response = mock_response(
            status_code=429, json_data={"text": "too many requests"}, headers={"Retry-After": "1"}
        )

        # Second response: success
        success_response = mock_response(status_code=200, json_data=TEST_ITEM)

        gw2_client.session.get.side_effect = [rate_limit_response, success_response]

        # This should handle the rate limit and retry
        item = await gw2_client.get_item(12345)

        assert item.id == 12345
        assert item.name == "Test Item"
        assert gw2_client.session.get.await_count == 2

    @pytest.mark.asyncio
    async def test_unauthorized_access(self, gw2_client, mock_response):
        """Test handling of unauthorized access."""
        gw2_client.session.get.return_value.__aenter__.return_value = mock_response(
            status_code=403, json_data={"text": "access denied"}
        )

        with pytest.raises(GW2APIUnauthorizedError):
            await gw2_client.get_account()

    @pytest.mark.asyncio
    async def test_get_item_success(self, gw2_client, mock_response):
        """Test successful item retrieval."""
        gw2_client.session.get.return_value.__aenter__.return_value = mock_response(
            status_code=200, json_data=TEST_ITEM
        )

        item = await gw2_client.get_item(12345)

        assert item.id == 12345
        assert item.name == "Test Item"
        assert item.type == "Weapon"
        assert item.rarity == "Exotic"
        assert item.vendor_value == 1000

    @pytest.mark.asyncio
    async def test_get_profession_success(self, gw2_client, mock_response):
        """Test successful profession retrieval."""
        gw2_client.session.get.return_value.__aenter__.return_value = mock_response(
            status_code=200, json_data=TEST_PROFESSION
        )

        profession = await gw2_client.get_profession("Elementalist")

        assert profession.id == "Elementalist"
        assert len(profession.weapons) > 0
        assert "Dagger" in profession.weapons
        assert "NoRacialSkills" in profession.flags


class TestGW2APIEndpoints:
    """Test suite for the GW2 API endpoints."""

    @pytest.mark.asyncio
    async def test_gw2_account_endpoint(self, test_app, mock_gw2_account):
        """Test the /gw2/account endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/v1/gw2/account", headers={"X-GW2-API-Key": "test-api-key"})

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-account-id"
        assert data["name"] == "Test Account"
        assert data["commander"] is True

    @pytest.mark.asyncio
    async def test_gw2_character_endpoint(self, test_app, mock_gw2_character):
        """Test the /gw2/characters/{name} endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                "/api/v1/gw2/characters/Test%20Character", headers={"X-GW2-API-Key": "test-api-key"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Character"
        assert data["profession"] == "Elementalist"

    @pytest.mark.asyncio
    async def test_gw2_item_endpoint(self, test_app, mock_gw2_item):
        """Test the /gw2/items/{id} endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/v1/gw2/items/12345")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 12345
        assert data["name"] == "Test Item"
        assert data["type"] == "Weapon"


# Fixtures for API endpoint tests
@pytest.fixture
def test_app(monkeypatch):
    """Fixture to provide a test FastAPI app with mocked GW2 client."""
    # This fixture ensures the app is properly set up for testing
    return app


@pytest.fixture
def mock_gw2_account(monkeypatch):
    """Mock the GW2 client's get_account method."""

    async def mock_get_account(self):
        return models.Account(**TEST_ACCOUNT)

    monkeypatch.setattr("app.api.api_v1.endpoints.gw2.GW2Client.get_account", mock_get_account)


@pytest.fixture
def mock_gw2_character(monkeypatch):
    """Mock the GW2 client's get_character method."""

    async def mock_get_character(self, character_name):
        return models.Character(**{**TEST_CHARACTER, "name": character_name})

    monkeypatch.setattr("app.api.api_v1.endpoints.gw2.GW2Client.get_character", mock_get_character)


@pytest.fixture
def mock_gw2_item(monkeypatch):
    """Mock the GW2 client's get_item method."""

    async def mock_get_item(self, item_id):
        return models.Item(**{**TEST_ITEM, "id": item_id})

    monkeypatch.setattr("app.api.api_v1.endpoints.gw2.GW2Client.get_item", mock_get_item)
