"""
Rate limiting configuration for the application.

This module configures FastAPILimiter with Redis for rate limiting.
"""

import logging
from typing import Callable

from fastapi import Request, HTTPException, status
from fastapi_limiter import FastAPILimiter

from app.core.config import settings

logger = logging.getLogger(__name__)


async def get_remote_id(request: Request) -> str:
    """
    Get a unique identifier for the client making the request.

    Args:
        request: The incoming request

    Returns:
        A string identifier for the client
    """
    try:
        # First try to get the user ID from the JWT token if available
        if "authorization" in request.headers:
            # This is a simplified example - in a real app, you would decode the JWT
            # and extract the user ID
            auth_header = request.headers["authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                # In a real implementation, you would decode the JWT here
                # and return the user ID
                # For now, we'll just use a placeholder
                return f"user:{token[:8]}"

        # Fall back to IP-based rate limiting
        if request.client is not None:
            return request.client.host
        return "unknown"
    except Exception as e:
        logger.warning(f"Error getting remote ID: {e}")
        # Fall back to IP-based rate limiting
        if request.client is not None:
            return request.client.host
        return "unknown"


async def init_rate_limiter() -> None:
    """Initialize the rate limiter with Redis."""
    try:
        if not settings.REDIS_URL:
            logger.warning("REDIS_URL not set, rate limiting will be disabled")
            return

        # Vérifier si le client Redis est disponible
        if not settings.redis_client:
            logger.warning("Redis client not available, rate limiting will be disabled")
            return

        # Initialiser le rate limiter
        await FastAPILimiter.init(settings.redis_client)
        logger.info("Rate limiter initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing rate limiter: {e}")
        if settings.ENVIRONMENT != "test":  # Ne pas échouer en environnement de test
            raise


async def close_rate_limiter() -> None:
    """Close the rate limiter connection."""
    try:
        if hasattr(FastAPILimiter, "redis") and FastAPILimiter.redis:
            await FastAPILimiter.redis.close()
            logger.info("Rate limiter connection closed")
    except Exception as e:
        logger.error(f"Error closing rate limiter: {e}")


# Rate limiting dependencies
def get_rate_limiter(times: int = 100, seconds: int = 60) -> Callable:
    """
    Get a rate limiter dependency.

    Args:
        times: Number of requests allowed in the time window
        seconds: Time window in seconds

    Returns:
        A dependency that can be used with FastAPI's Depends()
    """
    # Désactiver complètement le rate limiting en environnement de test
    if settings.ENVIRONMENT == "test" or not settings.REDIS_URL or not settings.CACHE_ENABLED:
        # Retourner une fonction vide qui ne fait rien
        async def noop_rate_limiter():
            return None

        return noop_rate_limiter

    # Create a rate limiter with the specified limits
    async def rate_limiter(request: Request):
        # Use the remote ID as the key for rate limiting
        key = f"rate_limit:{await get_remote_id(request)}"

        # Check if the rate limit has been exceeded
        current = await settings.redis_client.get(key)
        if current and int(current) >= times:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests, please try again later.",
                headers={"Retry-After": str(seconds)},
            )

        # Increment the rate limit counter
        pipe = settings.redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, seconds)
        await pipe.execute()

    return rate_limiter
