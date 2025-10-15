"""
Middlewares personnalisés pour l'API.

Ce module contient les middlewares personnalisés pour gérer les en-têtes de sécurité,
la journalisation des requêtes, la gestion des erreurs, etc.
"""

import json
import time
import uuid
from contextvars import ContextVar
from typing import Dict, Optional

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.core.config import settings
from app.core.logging import logger

# Variable de contexte pour stocker l'ID de requête
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour ajouter un ID unique à chaque requête.

    Cet ID est utilisé pour tracer les requêtes dans les logs et faciliter le débogage.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Générer un ID unique pour la requête
        request_id = str(uuid.uuid4())

        # Stocker l'ID dans la variable de contexte
        request_id_var.set(request_id)

        # Ajouter l'ID à l'objet de requête pour un accès facile
        request.state.request_id = request_id

        # Appeler le prochain middleware ou le gestionnaire de route
        response = await call_next(request)

        # Ajouter l'ID de requête dans les en-têtes de la réponse
        response.headers["X-Request-ID"] = request_id

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour journaliser les requêtes et les réponses.

    Enregistre les détails de chaque requête et réponse pour le débogage et l'audit.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Enregistrer le début de la requête
        start_time = time.time()
        request_id = (
            request.state.request_id if hasattr(request.state, "request_id") else ""
        )

        # Journaliser les détails de la requête
        logger.info(
            "Requête reçue",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "client": {"host": request.client.host if request.client else None},
            },
        )

        try:
            # Appeler le prochain middleware ou le gestionnaire de route
            response = await call_next(request)

            # Calculer le temps de traitement
            process_time = time.time() - start_time

            # Journaliser les détails de la réponse
            logger.info(
                "Réponse envoyée",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "process_time": process_time,
                    "headers": dict(response.headers),
                },
            )

            # Ajouter le temps de traitement dans les en-têtes
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            # En cas d'erreur, journaliser l'exception
            logger.exception(
                "Erreur lors du traitement de la requête",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "error_type": e.__class__.__name__,
                },
            )
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour ajouter des en-têtes de sécurité HTTP.

    Ajoute des en-têtes de sécurité recommandés pour protéger l'application
    contre diverses attaques (XSS, clickjacking, etc.).
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:;",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        }

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Appeler le prochain middleware ou le gestionnaire de route
        response = await call_next(request)

        # Ajouter les en-têtes de sécurité à la réponse
        for header, value in self.security_headers.items():
            if header not in response.headers:
                response.headers[header] = value

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour limiter le taux de requêtes.

    Implémente une limitation de débit basique pour éviter les abus.
    """

    def __init__(
        self,
        app: ASGIApp,
        limit: int = 100,
        window: int = 60,  # secondes
    ) -> None:
        super().__init__(app)
        self.limit = limit
        self.window = window
        self.requests: Dict[str, list] = {}

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Ne pas appliquer la limitation pour les routes publiques
        if any(
            request.url.path.startswith(path)
            for path in ["/docs", "/redoc", "/openapi.json", "/health"]
        ):
            return await call_next(request)

        # Récupérer l'adresse IP du client
        client_ip = request.client.host if request.client else "unknown"
        current_time = int(time.time())

        # Nettoyer les anciennes entrées
        self.requests[client_ip] = [
            t
            for t in self.requests.get(client_ip, [])
            if t > current_time - self.window
        ]

        # Vérifier si le taux est dépassé
        if len(self.requests.get(client_ip, [])) >= self.limit:
            return Response(
                content=json.dumps({"detail": "Trop de requêtes"}),
                status_code=429,
                headers={"Retry-After": str(self.window)},
                media_type="application/json",
            )

        # Ajouter la requête actuelle
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        self.requests[client_ip].append(current_time)

        # Appeler le prochain middleware ou le gestionnaire de route
        response = await call_next(request)

        # Ajouter des en-têtes de quota
        remaining = max(0, self.limit - len(self.requests[client_ip]))
        response.headers["X-RateLimit-Limit"] = str(self.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(current_time + self.window)

        return response


def setup_middlewares(app: FastAPI) -> None:
    """
    Configure les middlewares de l'application.

    Args:
        app: L'application FastAPI
    """
    # Middleware CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Middleware de compression GZIP
    app.add_middleware(GZipMiddleware, minimum_size=500)

    # Redirection HTTP vers HTTPS en production
    if not settings.DEBUG and not settings.TESTING:
        app.add_middleware(HTTPSRedirectMiddleware)

    # Ajouter les middlewares personnalisés
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)

    # Activer la limitation de débit uniquement en production
    if not settings.DEBUG and not settings.TESTING:
        app.add_middleware(
            RateLimitMiddleware, limit=100, window=60
        )  # 100 requêtes/minute par IP
