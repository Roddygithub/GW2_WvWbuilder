"""
Guild Wars 2 API Client

This module provides a client for interacting with the Guild Wars 2 API (v2).
It handles authentication, rate limiting, and response caching.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type, TypeVar

import aiohttp
import backoff
from pydantic import ValidationError

from . import models
from .cache import GW2Cache
from .exceptions import (
    GW2APIError,
    GW2APINotFoundError,
    GW2APIUnauthorizedError,
    GW2APIRateLimitError,
    GW2APIUnavailableError,
    GW2APIValidationError,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=models.BaseModel)


class GW2Client:
    """Client for interacting with the Guild Wars 2 API."""

    BASE_URL = "https://api.guildwars2.com/v2"
    DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=30)

    def __init__(
        self,
        api_key: Optional[str] = None,
        session: Optional[aiohttp.ClientSession] = None,
        cache: Optional[GW2Cache] = None,
        language: str = "en",
        schema_version: str = "2022-03-23T00:00:00Z",
    ):
        """Initialize the GW2 API client.

        Args:
            api_key: Optional API key for authenticated endpoints.
            session: Optional aiohttp ClientSession to use for requests.
            cache: Optional cache instance for API responses.
            language: Language code for localized content (e.g., 'en', 'fr', 'de').
            schema_version: API schema version to use.
        """
        self.api_key = api_key
        self.language = language
        self.schema_version = schema_version
        self._session = session
        self._cache = cache
        self._rate_limit_remaining = 300  # Default rate limit
        self._rate_limit_reset = 0

    async def __aenter__(self):
        """Async context manager entry."""
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self.DEFAULT_TIMEOUT)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session and not self._session.closed:
            await self._session.close()

    @property
    def session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.DEFAULT_TIMEOUT)
        return self._session

    @property
    def cache(self) -> GW2Cache:
        """Get the cache instance, creating one if needed."""
        if self._cache is None:
            # This is a fallback - in a FastAPI app, you should use dependency injection
            self._cache = GW2Cache()
        return self._cache

    def _get_headers(self) -> Dict[str, str]:
        """Get default headers for API requests."""
        headers = {
            "Accept": "application/json",
            "Accept-Language": self.language,
            "X-Schema-Version": self.schema_version,
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        jitter=backoff.full_jitter,
    )
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        model: Optional[Type[T]] = None,
        cache_ttl: int = 3600,
    ) -> Any:
        """Make an HTTP request to the GW2 API with retry logic."""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"

        # Check cache for GET requests
        cache_key = None
        if method.upper() == "GET" and not endpoint.startswith("account"):
            cache_key = self.cache._get_key(endpoint, params)
            if model and (cached := await self.cache.get(cache_key, model)):
                return cached

        # Check rate limiting
        await self._check_rate_limit()

        # Make the request
        try:
            async with self.session.request(
                method,
                url,
                params=params,
                headers=self._get_headers(),
            ) as response:
                # Update rate limit information
                self._update_rate_limits(response)

                # Handle response
                if response.status == 200:
                    data = await response.json()

                    # Validate and cache the response if a model is provided
                    if model:
                        try:
                            result = model.parse_obj(data)
                            if cache_key:
                                await self.cache.set(cache_key, result, ttl=cache_ttl)
                            return result
                        except ValidationError as e:
                            logger.error(f"Validation error for {url}: {e}")
                            raise GW2APIError(f"Invalid response format: {e}") from e
                    return data

                # Handle errors
                await self._handle_error(response)

        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            raise GW2APIUnavailableError("Service temporarily unavailable") from e

    def _update_rate_limits(self, response: aiohttp.ClientResponse) -> None:
        """Update rate limit information from response headers."""
        if "X-Rate-Limit-Limit" in response.headers:
            self._rate_limit_remaining = int(
                response.headers.get("X-Rate-Limit-Remaining", 300)
            )
            self._rate_limit_reset = int(response.headers.get("X-Rate-Limit-Reset", 0))

    async def _check_rate_limit(self) -> None:
        """Check if we're approaching the rate limit and wait if needed."""
        if self._rate_limit_remaining < 10:  # Leave some buffer
            reset_time = self._rate_limit_reset - int(
                datetime.now(timezone.utc).timestamp()
            )
            if reset_time > 0:
                logger.warning(f"Approaching rate limit, waiting {reset_time} seconds")
                await asyncio.sleep(reset_time + 1)  # Add a small buffer

    async def _handle_error(self, response: aiohttp.ClientResponse) -> None:
        """Handle API errors and raise appropriate exceptions."""
        try:
            error_data = await response.json()
            error_text = error_data.get("text", "Unknown error")
        except (ValueError, aiohttp.ContentTypeError):
            error_text = await response.text() or "Unknown error"

        if response.status == 400:
            raise GW2APIValidationError(f"Bad request: {error_text}")
        elif response.status == 401:
            raise GW2APIUnauthorizedError(
                "Authentication failed: Invalid or missing API key"
            )
        elif response.status == 403:
            raise GW2APIUnauthorizedError("Insufficient permissions for this endpoint")
        elif response.status == 404:
            raise GW2APINotFoundError("The requested resource was not found")
        elif response.status == 429:
            retry_after = int(response.headers.get("Retry-After", 5))
            logger.warning(f"Rate limited, waiting {retry_after} seconds")
            raise GW2APIRateLimitError("Rate limit exceeded")
        elif 500 <= response.status < 600:
            raise GW2APIUnavailableError(
                f"Server error: {response.status} {error_text}"
            )
        else:
            raise GW2APIError(f"Unexpected error: {response.status} {error_text}")

    # Public API Methods

    # Account Endpoints
    async def get_account(self) -> models.Account:
        """Get the account information for the authenticated user."""
        if not self.api_key:
            raise GW2APIUnauthorizedError("API key is required for account endpoints")
        return await self._request("GET", "account", model=models.Account)

    async def get_characters(self) -> List[str]:
        """Get the list of character names for the authenticated account."""
        if not self.api_key:
            raise GW2APIUnauthorizedError("API key is required for character endpoints")
        return await self._request("GET", "characters")

    async def get_character(self, character_name: str) -> models.Character:
        """Get detailed information about a specific character."""
        if not self.api_key:
            raise GW2APIUnauthorizedError("API key is required for character endpoints")
        endpoint = f"characters/{character_name}"
        return await self._request("GET", endpoint, model=models.Character)

    # Items and Trading Post
    async def get_item(self, item_id: int) -> models.Item:
        """Get information about an item by its ID."""
        return await self._request("GET", f"items/{item_id}", model=models.Item)

    async def get_items(self, item_ids: List[int]) -> List[models.Item]:
        """Get multiple items by their IDs."""
        if not item_ids:
            return []
        params = {"ids": ",".join(str(i) for i in item_ids)}
        data = await self._request("GET", "items", params=params)
        return [models.Item.parse_obj(item) for item in data]

    async def get_item_price(self, item_id: int) -> models.ItemPrice:
        """Get the current trading post prices for an item."""
        return await self._request(
            "GET", f"commerce/prices/{item_id}", model=models.ItemPrice
        )

    # Game Data
    async def get_professions(self) -> List[str]:
        """Get a list of all profession IDs."""
        return await self._request("GET", "professions")

    async def get_profession(self, profession_id: str) -> models.Profession:
        """Get detailed information about a profession."""
        return await self._request(
            "GET", f"professions/{profession_id}", model=models.Profession
        )

    async def get_skills(self, skill_ids: List[int]) -> List[models.Skill]:
        """Get information about multiple skills by their IDs."""
        if not skill_ids:
            return []
        params = {"ids": ",".join(str(i) for i in skill_ids)}
        data = await self._request("GET", "skills", params=params)
        return [models.Skill.parse_obj(skill) for skill in data]

    async def get_traits(self, trait_ids: List[int]) -> List[models.Trait]:
        """Get information about multiple traits by their IDs."""
        if not trait_ids:
            return []
        params = {"ids": ",".join(str(i) for i in trait_ids)}
        data = await self._request("GET", "traits", params=params)
        return [models.Trait.parse_obj(trait) for trait in data]

    # Build and Equipment
    async def get_equipment_tabs(self) -> List[models.EquipmentTab]:
        """Get the equipment tabs for the authenticated account."""
        if not self.api_key:
            raise GW2APIUnauthorizedError(
                "API key is required for equipment tab endpoints"
            )
        data = await self._request("GET", "account/bank")
        return [models.EquipmentTab.parse_obj(tab) for tab in data]

    async def get_build_tabs(self) -> List[models.BuildTab]:
        """Get the build tabs for the authenticated account."""
        if not self.api_key:
            raise GW2APIUnauthorizedError("API key is required for build tab endpoints")
        data = await self._request("GET", "account/build")
        return [models.BuildTab.parse_obj(tab) for tab in data]

    # Utility Methods
    async def search_items(self, name: str) -> List[models.Item]:
        """Search for items by name."""
        # First get all item IDs that match the name
        params = {"name": name}
        item_ids = await self._request("GET", "items/search", params=params)

        # Then fetch the full item details
        if not item_ids:
            return []
        return await self.get_items(item_ids)


# Dependency for FastAPI
def get_gw2_client(
    api_key: Optional[str] = None,
    language: str = "en",
    schema_version: str = "2022-03-23T00:00:00Z",
) -> GW2Client:
    """Dependency to get a GW2Client instance."""
    return GW2Client(
        api_key=api_key,
        language=language,
        schema_version=schema_version,
    )
