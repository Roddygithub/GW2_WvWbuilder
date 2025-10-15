"""
Module d'optimisation des performances de l'application.

Ce module fournit des utilitaires pour optimiser les performances de l'application,
y compris la mise en cache, le rate limiting et la gestion des connexions.
"""

import time
from functools import wraps
from typing import Any, Callable, TypeVar, cast

from fastapi import Request, Response
from fastapi.concurrency import run_in_threadpool
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.core.config import settings

# Type variable for generic function typing
F = TypeVar("F", bound=Callable[..., Any])


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware pour mesurer et optimiser les performances des requêtes."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.time()

        # Ajouter des en-têtes de performance
        response = await call_next(request)

        # Calculer le temps de traitement
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        # En-têtes de cache
        if request.method == "GET":
            response.headers["Cache-Control"] = "public, max-age=300"

        return response


class CachedRoute(APIRoute):
    """Route avec mise en cache intégrée."""

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            # Logique de mise en cache ici
            # Pour l'instant, on passe simplement à travers
            response = await original_route_handler(request)
            return response

        return custom_route_handler


def cache_response(ttl: int = 300) -> Callable[[F], F]:
    """Décorateur pour mettre en cache la réponse d'une fonction.

    Args:
        ttl: Durée de vie du cache en secondes
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Logique de mise en cache à implémenter
            result = await func(*args, **kwargs)
            return result

        return cast(F, wrapper)

    return decorator


async def run_in_threadpool_if_needed(
    func: Callable[..., Any], *args: Any, **kwargs: Any
) -> Any:
    """Exécute une fonction de manière asynchrone ou dans un thread si nécessaire."""
    if not settings.TESTING and not settings.DEBUG:
        return await run_in_threadpool(func, *args, **kwargs)
    return func(*args, **kwargs)


def setup_performance_middleware(app: ASGIApp) -> None:
    """Configure les middlewares de performance."""
    app.add_middleware(PerformanceMiddleware)
