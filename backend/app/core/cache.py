"""
Cache module for Redis integration.

This module provides a simple interface for caching data in Redis.
"""
from typing import Any, Optional, Union, Callable, TypeVar, cast
import json
import pickle
from functools import wraps
import logging

from redis.asyncio import Redis
from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder

from .config import settings

# Type variable for generic function return type
T = TypeVar('T')

# Initialize logger
logger = logging.getLogger(__name__)

class CacheManager:
    """Manager for Redis cache operations."""
    
    def __init__(self):
        """Initialize the Redis client."""
        self.redis: Optional[Redis] = None
        self.enabled = settings.CACHE_ENABLED
    
    async def init_redis(self):
        """Initialize the Redis connection."""
        if not self.enabled:
            return
            
        try:
            self.redis = Redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            # Test the connection
            await self.redis.ping()
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            self.enabled = False
            self.redis = None
    
    async def close(self):
        """Close the Redis connection."""
        if self.redis:
            await self.redis.close()
            await self.redis.connection_pool.disconnect()
            logger.info("Redis connection closed")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        if not self.enabled or not self.redis:
            return None
            
        try:
            value = await self.redis.get(key)
            if value is None:
                return None
                
            try:
                # Try to deserialize JSON first
                return json.loads(value)
            except json.JSONDecodeError:
                # Fall back to pickle for complex objects
                return pickle.loads(value.encode('latin1'))
        except Exception as e:
            logger.error(f"Error getting key {key} from cache: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set a value in the cache with an optional TTL (in seconds)."""
        if not self.enabled or not self.redis:
            return False
            
        try:
            # Use JSON for basic types, fall back to pickle for complex objects
            try:
                serialized = json.dumps(jsonable_encoder(value))
            except (TypeError, OverflowError):
                serialized = pickle.dumps(value).decode('latin1')
                
            if ttl is None:
                ttl = settings.CACHE_TTL
                
            await self.redis.set(key, serialized, ex=ttl)
            return True
        except Exception as e:
            logger.error(f"Error setting key {key} in cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete a key from the cache."""
        if not self.enabled or not self.redis:
            return False
            
        try:
            return await self.redis.delete(key) > 0
        except Exception as e:
            logger.error(f"Error deleting key {key} from cache: {e}")
            return False
    
    async def clear(self, pattern: str = "*") -> int:
        """Clear all keys matching the pattern."""
        if not self.enabled or not self.redis:
            return 0
            
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error clearing cache with pattern {pattern}: {e}")
            return 0
    
    async def invalidate_team(self, team_id: int) -> bool:
        """Invalidate all cache entries for a team."""
        return await self.clear(f"team:{team_id}:*") > 0
    
    async def invalidate_user(self, user_id: int) -> bool:
        """Invalidate all cache entries for a user."""
        return await self.clear(f"user:{user_id}:*") > 0
    
    async def invalidate_composition(self, composition_id: int) -> bool:
        """Invalidate all cache entries for a composition."""
        return await self.clear(f"composition:{composition_id}:*") > 0


# Global cache instance
cache = CacheManager()


def cached(
    key_pattern: Optional[str] = None, 
    ttl: Optional[int] = None,
    unless: Optional[Callable[..., bool]] = None
):
    """
    Decorator to cache the result of an async function.
    
    Args:
        key_pattern: Pattern for the cache key. Use {arg} for argument substitution.
                    If None, uses 'function_name:arg1:arg2:...'.
        ttl: Time to live in seconds. Uses default if None.
        unless: Callable that returns True to skip caching.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Skip caching if disabled
            if not cache.enabled:
                return await func(*args, **kwargs)
                
            # Check if we should skip caching
            if unless and unless(*args, **kwargs):
                return await func(*args, **kwargs)
            
            # Generate cache key
            if key_pattern:
                # Format the key pattern with the function arguments
                bound_arguments = {}
                if args and hasattr(func, '__self__'):
                    # Handle instance methods
                    bound_arguments = func.__code__.co_varnames[1:len(args)]
                    bound_arguments = dict(zip(bound_arguments, args[1:]))
                elif args:
                    # Handle regular functions
                    bound_arguments = dict(zip(func.__code__.co_varnames[:len(args)], args))
                bound_arguments.update(kwargs)
                
                try:
                    cache_key = key_pattern.format(**bound_arguments)
                except KeyError as e:
                    logger.warning(f"Could not format cache key: {e}, skipping cache")
                    return await func(*args, **kwargs)
            else:
                # Default key format: function_name:arg1:arg2:...
                cache_key = f"{func.__module__}:{func.__name__}:" + ":".join(
                    str(arg) for arg in args[1:] if isinstance(arg, (str, int, float, bool))
                )
                if kwargs:
                    cache_key += ":" + ":".join(
                        f"{k}={v}" for k, v in sorted(kwargs.items())
                        if isinstance(v, (str, int, float, bool))
                    )
            
            # Try to get from cache
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result
                
            # Call the function and cache the result
            result = await func(*args, **kwargs)
            
            # Cache the result if it's not None
            if result is not None:
                await cache.set(cache_key, result, ttl=ttl)
                
            return result
        
        return wrapper
    return decorator
