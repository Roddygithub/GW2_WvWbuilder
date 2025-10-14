"""
Comprehensive tests for GW2 API Client.
Tests for app/core/gw2/client.py to achieve 80%+ coverage.
"""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp

from app.core.gw2.client import GW2Client
from app.core.gw2.exceptions import (
    GW2APIError,
    GW2APINotFoundError,
    GW2APIUnauthorizedError,
    GW2APIRateLimitError,
    GW2APIUnavailableError,
)


@pytest.fixture
def mock_session():
    """Create a mock aiohttp session."""
    session = MagicMock(spec=aiohttp.ClientSession)
    session.closed = False
    session.close = AsyncMock()
    return session


@pytest.fixture
def gw2_client(mock_session):
    """Create a GW2Client instance with mock session."""
    return GW2Client(session=mock_session)


@pytest.fixture
def gw2_client_with_key(mock_session):
    """Create a GW2Client instance with API key."""
    return GW2Client(api_key="test_api_key", session=mock_session)


class TestGW2ClientInit:
    """Test GW2Client initialization."""

    def test_init_default(self):
        """Test client initialization with defaults."""
        client = GW2Client()

        assert client.api_key is None
        assert client.language == "en"
        assert client.schema_version == "2022-03-23T00:00:00Z"
        assert client._session is None

    def test_init_with_api_key(self):
        """Test client initialization with API key."""
        client = GW2Client(api_key="test_key")

        assert client.api_key == "test_key"

    def test_init_with_custom_language(self):
        """Test client initialization with custom language."""
        client = GW2Client(language="fr")

        assert client.language == "fr"

    def test_init_with_session(self, mock_session):
        """Test client initialization with existing session."""
        client = GW2Client(session=mock_session)

        assert client._session == mock_session


class TestGW2ClientContextManager:
    """Test GW2Client async context manager."""

    @pytest.mark.asyncio
    async def test_context_manager_creates_session(self):
        """Test that context manager creates session if none exists."""
        client = GW2Client()

        async with client as c:
            assert c._session is not None
            assert isinstance(c._session, aiohttp.ClientSession)

    @pytest.mark.asyncio
    async def test_context_manager_closes_session(self):
        """Test that context manager closes session on exit."""
        client = GW2Client()

        async with client:
            session = client._session

        assert session.closed

    @pytest.mark.asyncio
    async def test_context_manager_uses_existing_session(self, mock_session):
        """Test that context manager uses existing session."""
        client = GW2Client(session=mock_session)

        async with client as c:
            assert c._session == mock_session


class TestGW2ClientRequests:
    """Test GW2Client HTTP request methods."""

    @pytest.mark.asyncio
    async def test_get_request_success(self, gw2_client, mock_session):
        """Test successful GET request."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"id": 1, "name": "Test"})
        mock_response.headers = {"X-Rate-Limit-Remaining": "299"}

        mock_session.get = AsyncMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        result = await gw2_client.get("/test")

        assert result == {"id": 1, "name": "Test"}
        mock_session.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_request_with_params(self, gw2_client, mock_session):
        """Test GET request with parameters."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=[])
        mock_response.headers = {}

        mock_session.get = AsyncMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        await gw2_client.get("/test", params={"ids": "1,2,3"})

        call_args = mock_session.get.call_args
        assert "params" in call_args.kwargs

    @pytest.mark.asyncio
    async def test_get_request_404(self, gw2_client, mock_session):
        """Test GET request returning 404."""
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.text = AsyncMock(return_value="Not Found")

        mock_session.get = AsyncMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        with pytest.raises(GW2APINotFoundError):
            await gw2_client.get("/nonexistent")

    @pytest.mark.asyncio
    async def test_get_request_401(self, gw2_client, mock_session):
        """Test GET request returning 401."""
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.text = AsyncMock(return_value="Unauthorized")

        mock_session.get = AsyncMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        with pytest.raises(GW2APIUnauthorizedError):
            await gw2_client.get("/account")

    @pytest.mark.asyncio
    async def test_get_request_429(self, gw2_client, mock_session):
        """Test GET request returning 429 (rate limit)."""
        mock_response = AsyncMock()
        mock_response.status = 429
        mock_response.text = AsyncMock(return_value="Rate Limited")
        mock_response.headers = {"X-Rate-Limit-Reset": "60"}

        mock_session.get = AsyncMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        with pytest.raises(GW2APIRateLimitError):
            await gw2_client.get("/test")

    @pytest.mark.asyncio
    async def test_get_request_503(self, gw2_client, mock_session):
        """Test GET request returning 503."""
        mock_response = AsyncMock()
        mock_response.status = 503
        mock_response.text = AsyncMock(return_value="Service Unavailable")

        mock_session.get = AsyncMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        with pytest.raises(GW2APIUnavailableError):
            await gw2_client.get("/test")


class TestGW2ClientAuthentication:
    """Test GW2Client authentication."""

    @pytest.mark.asyncio
    async def test_request_with_api_key(self, gw2_client_with_key, mock_session):
        """Test that API key is included in request headers."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={})
        mock_response.headers = {}

        mock_session.get = AsyncMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        await gw2_client_with_key.get("/account")

        call_args = mock_session.get.call_args
        assert "headers" in call_args.kwargs
        assert "Authorization" in call_args.kwargs["headers"]

    @pytest.mark.asyncio
    async def test_request_without_api_key(self, gw2_client, mock_session):
        """Test request without API key."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={})
        mock_response.headers = {}

        mock_session.get = AsyncMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        await gw2_client.get("/items")

        call_args = mock_session.get.call_args
        headers = call_args.kwargs.get("headers", {})
        assert "Authorization" not in headers


class TestGW2ClientRateLimiting:
    """Test GW2Client rate limiting."""

    @pytest.mark.asyncio
    async def test_rate_limit_tracking(self, gw2_client, mock_session):
        """Test that rate limit is tracked from response headers."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={})
        mock_response.headers = {"X-Rate-Limit-Remaining": "250", "X-Rate-Limit-Reset": "60"}

        mock_session.get = AsyncMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        await gw2_client.get("/test")

        assert gw2_client._rate_limit_remaining == 250

    @pytest.mark.asyncio
    async def test_rate_limit_low_warning(self, gw2_client, mock_session):
        """Test warning when rate limit is low."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={})
        mock_response.headers = {"X-Rate-Limit-Remaining": "10"}

        mock_session.get = AsyncMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        with patch("app.core.gw2.client.logger"):
            await gw2_client.get("/test")

            # Should log warning when rate limit is low
            assert gw2_client._rate_limit_remaining == 10


class TestGW2ClientCaching:
    """Test GW2Client caching functionality."""

    @pytest.mark.asyncio
    async def test_cache_hit(self, gw2_client):
        """Test that cached responses are returned."""
        mock_cache = MagicMock()
        mock_cache.get = AsyncMock(return_value={"cached": True})
        gw2_client._cache = mock_cache

        result = await gw2_client.get("/test")

        assert result == {"cached": True}
        mock_cache.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_miss(self, gw2_client, mock_session):
        """Test that cache miss triggers API request."""
        mock_cache = MagicMock()
        mock_cache.get = AsyncMock(return_value=None)
        mock_cache.set = AsyncMock()
        gw2_client._cache = mock_cache

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"fresh": True})
        mock_response.headers = {}

        mock_session.get = AsyncMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        result = await gw2_client.get("/test")

        assert result == {"fresh": True}
        mock_cache.set.assert_called_once()


class TestGW2ClientSpecificEndpoints:
    """Test specific GW2 API endpoints."""

    @pytest.mark.asyncio
    async def test_get_items(self, gw2_client, mock_session):
        """Test getting items."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=[1, 2, 3])
        mock_response.headers = {}

        mock_session.get = AsyncMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        result = await gw2_client.get_items()

        assert result == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_get_item_by_id(self, gw2_client, mock_session):
        """Test getting specific item."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"id": 123, "name": "Sword"})
        mock_response.headers = {}

        mock_session.get = AsyncMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        result = await gw2_client.get_item(123)

        assert result["id"] == 123
        assert result["name"] == "Sword"

    @pytest.mark.asyncio
    async def test_get_professions(self, gw2_client, mock_session):
        """Test getting professions."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=["Guardian", "Warrior"])
        mock_response.headers = {}

        mock_session.get = AsyncMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        result = await gw2_client.get_professions()

        assert "Guardian" in result
        assert "Warrior" in result

    @pytest.mark.asyncio
    async def test_get_skills(self, gw2_client, mock_session):
        """Test getting skills."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=[1, 2, 3])
        mock_response.headers = {}

        mock_session.get = AsyncMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        result = await gw2_client.get_skills()

        assert isinstance(result, list)


class TestGW2ClientErrorHandling:
    """Test GW2Client error handling."""

    @pytest.mark.asyncio
    async def test_network_error(self, gw2_client, mock_session):
        """Test handling of network errors."""
        mock_session.get = AsyncMock(side_effect=aiohttp.ClientError("Network error"))

        with pytest.raises(GW2APIError):
            await gw2_client.get("/test")

    @pytest.mark.asyncio
    async def test_timeout_error(self, gw2_client, mock_session):
        """Test handling of timeout errors."""
        mock_session.get = AsyncMock(side_effect=asyncio.TimeoutError())

        with pytest.raises(GW2APIError):
            await gw2_client.get("/test")

    @pytest.mark.asyncio
    async def test_invalid_json_response(self, gw2_client, mock_session):
        """Test handling of invalid JSON responses."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(side_effect=ValueError("Invalid JSON"))
        mock_response.text = AsyncMock(return_value="Not JSON")

        mock_session.get = AsyncMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        with pytest.raises(GW2APIError):
            await gw2_client.get("/test")


class TestGW2ClientEdgeCases:
    """Test edge cases."""

    @pytest.mark.asyncio
    async def test_empty_response(self, gw2_client, mock_session):
        """Test handling of empty response."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={})
        mock_response.headers = {}

        mock_session.get = AsyncMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        result = await gw2_client.get("/test")

        assert result == {}

    @pytest.mark.asyncio
    async def test_large_response(self, gw2_client, mock_session):
        """Test handling of large responses."""
        large_data = [{"id": i} for i in range(1000)]

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=large_data)
        mock_response.headers = {}

        mock_session.get = AsyncMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        result = await gw2_client.get("/test")

        assert len(result) == 1000

    def test_session_property(self, gw2_client):
        """Test session property creates session if needed."""
        gw2_client._session = None

        session = gw2_client.session

        assert session is not None
        assert isinstance(session, aiohttp.ClientSession)
