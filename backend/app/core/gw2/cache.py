"""
GW2 API Caching Module

This module provides a caching layer for GW2 API responses to reduce API calls
and improve performance. It uses Redis for distributed caching if available,
with an in-memory fallback.
"""

import json
import time
from typing import Any, Optional, TypeVar, Type, Dict
import hashlib
import logging

from pydantic import BaseModel
import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class GW2Cache:
    """GW2 API response cache with Redis backend."""

    def __init__(
        self, redis_client: Optional[redis.Redis] = None, prefix: str = "gw2:"
    ):
        """Initialize the cache with an optional Redis client.

        Args:
            redis_client: Optional Redis client. If not provided, uses in-memory cache.
            prefix: Prefix for all cache keys.
        """
        self.redis = redis_client
        self.prefix = prefix
        self.memory_cache: Dict[str, tuple[float, Any]] = {}

    def _get_key(self, endpoint: str, params: Optional[dict] = None) -> str:
        """Generate a cache key from endpoint and parameters."""
        key_parts = [self.prefix, endpoint]
        if params:
            # Sort params to ensure consistent key generation
            sorted_params = json.dumps(params, sort_keys=True)
            key_parts.append(hashlib.sha256(sorted_params.encode()).hexdigest())
        return ":".join(key_parts)

    async def get(self, key: str, model: Type[T]) -> Optional[T]:
        """Get a cached item by key."""
        # First try Redis if available
        if self.redis is not None:
            try:
                cached = await self.redis.get(key)
                if cached:
                    return model.parse_raw(cached)
            except Exception as e:
                logger.warning(f"Redis cache error: {e}")

        # Fall back to in-memory cache
        if key in self.memory_cache:
            expiry, data = self.memory_cache[key]
            if time.time() < expiry:
                return model.parse_obj(data)
            del self.memory_cache[key]

        return None

    async def set(self, key: str, value: BaseModel, ttl: int = 3600) -> None:
        """Cache an item with a time-to-live in seconds."""
        serialized = value.json()

        # Try Redis first if available
        if self.redis is not None:
            try:
                await self.redis.set(key, serialized, ex=ttl)
                return
            except Exception as e:
                logger.warning(f"Redis cache error: {e}")

        # Fall back to in-memory cache
        self.memory_cache[key] = (time.time() + ttl, value.dict())

    async def invalidate(self, pattern: str) -> None:
        """Invalidate cache entries matching a pattern."""
        if self.redis is not None:
            try:
                keys = await self.redis.keys(f"{self.prefix}{pattern}*")
                if keys:
                    await self.redis.delete(*keys)
            except Exception as e:
                logger.warning(f"Error invalidating Redis cache: {e}")

        # Also clear matching in-memory cache entries
        for key in list(self.memory_cache.keys()):
            if key.startswith(f"{self.prefix}{pattern}"):
                del self.memory_cache[key]


# Create a global cache instance
gw2_cache: Optional[GW2Cache] = None


async def get_gw2_cache() -> GW2Cache:
    """Dependency to get the GW2 cache instance."""
    global gw2_cache

    if gw2_cache is None:
        # Initialize Redis client if Redis is configured
        redis_client = None
        if settings.REDIS_URL:
            try:
                redis_client = redis.from_url(settings.REDIS_URL)
                # Test the connection
                await redis_client.ping()
            except Exception as e:
                logger.warning(
                    f"Failed to connect to Redis: {e}. Using in-memory cache."
                )
                redis_client = None

        gw2_cache = GW2Cache(redis_client=redis_client)

    return gw2_cache
