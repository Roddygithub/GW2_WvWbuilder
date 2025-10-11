import json
from functools import wraps
from typing import Callable, Any, Optional

from fastapi import Request, Response
from app.core.config import settings
from prometheus_client import Counter

# Prometheus metrics for cache
CACHE_HITS = Counter("cache_hits_total", "Total number of cache hits", ["endpoint"])
CACHE_MISSES = Counter("cache_misses_total", "Total number of cache misses", ["endpoint"])


def cache_response(ttl: int = settings.CACHE_TTL) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Décorateur pour mettre en cache la réponse d'une route FastAPI dans Redis.

    Args:
        ttl (int): Durée de vie du cache en secondes.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            request: Optional[Request] = kwargs.get("request")
            response_obj: Optional[Response] = kwargs.get("response")

            if not settings.CACHE_ENABLED or request is None:
                return await func(*args, **kwargs)

            endpoint_path = request.url.path
            cache_key = f"cache:{endpoint_path}:{request.url.query}"
            cached_response = await settings.redis_client.get(cache_key)

            if cached_response:
                CACHE_HITS.labels(endpoint=endpoint_path).inc()
                if response_obj:
                    response_obj.headers["X-Cache"] = "HIT"
                return json.loads(cached_response)

            CACHE_MISSES.labels(endpoint=endpoint_path).inc()
            result = await func(*args, **kwargs)

            if response_obj:
                response_obj.headers["X-Cache"] = "MISS"
            # Pydantic models need to be converted to dicts before json.dumps
            await settings.redis_client.setex(
                cache_key, ttl, json.dumps(result, default=lambda o: o.dict() if hasattr(o, "dict") else str(o))
            )
            return result

        return wrapper

    return decorator


# Initialize Redis client for caching
cache = settings.redis_client
