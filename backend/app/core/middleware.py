"""
Middlewares personnalisés pour l'application FastAPI.
"""

import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.core.logging import logger
from app.core.config import settings


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour ajouter un ID unique à chaque requête.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour mesurer le temps de traitement des requêtes.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        # Log des performances
        logger.info(
            "Request processed",
            extra={
                "request_id": getattr(request.state, "request_id", ""),
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time": process_time,
            },
        )

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour ajouter des en-têtes de sécurité HTTP.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)

        # En-têtes de sécurité
        security_headers = {
            # Protection contre le détournement de type MIME
            "X-Content-Type-Options": "nosniff",
            # Protection contre le clickjacking
            "X-Frame-Options": "DENY",
            # Protection XSS (obsolète mais gardé pour la rétrocompatibilité)
            "X-XSS-Protection": "1; mode=block",
            # Politique de référent
            "Referrer-Policy": "strict-origin-when-cross-origin",
            # Politique de sécurité du contenu (CSP)
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://fonts.gstatic.com; "
                "connect-src 'self' https://api.gw2w2builder.com; "
                "frame-ancestors 'none'; "
                "form-action 'self'; "
                "base-uri 'self'; "
                "object-src 'none'"
            ),
            # HSTS - Force HTTPS
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            # Permissions Policy (anciennement Feature Policy)
            "Permissions-Policy": (
                "accelerometer=(), "
                "camera=(), "
                "geolocation=(), "
                "gyroscope=(), "
                "magnetometer=(), "
                "microphone=(), "
                "payment=(), "
                "usb=()"
            ),
            # Cross-Origin Embedder Policy
            "Cross-Origin-Embedder-Policy": "require-corp",
            # Cross-Origin Opener Policy
            "Cross-Origin-Opener-Policy": "same-origin",
            # Cross-Origin Resource Policy
            "Cross-Origin-Resource-Policy": "same-site",
        }

        # Ajout des en-têtes à la réponse
        for header, value in security_headers.items():
            response.headers[header] = value

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour limiter le taux de requêtes.
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
        self.requests = {}

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Ne pas appliquer la limitation de taux pour certaines routes
        if any(
            request.url.path.startswith(path)
            for path in ["/docs", "/redoc", "/openapi.json", "/metrics"]
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
                content={"detail": "Too many requests"},
                status_code=429,
                headers={"Retry-After": str(self.window)},
            )

        # Ajouter la requête actuelle
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        self.requests[client_ip].append(current_time)

        # Appeler le prochain middleware/gestionnaire
        response = await call_next(request)

        # Ajouter des en-têtes de quota
        remaining = max(0, self.limit - len(self.requests[client_ip]))
        response.headers["X-RateLimit-Limit"] = str(self.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(current_time + self.window)

        return response


def setup_middlewares(app: ASGIApp) -> None:
    """
    Configure les middlewares de l'application.

    Args:
        app: L'application FastAPI
    """
    # Configuration CORS
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

    # Middleware CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time"],
        max_age=600,  # 10 minutes
    )

    # Redirection HTTP vers HTTPS en production
    if not settings.DEBUG and not settings.TESTING:
        app.add_middleware(HTTPSRedirectMiddleware)

    # Ajout des autres middlewares
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)

    # Activation de la limitation de taux uniquement en production
    if not settings.DEBUG and not settings.TESTING:
        app.add_middleware(
            RateLimitMiddleware, limit=100, window=60
        )  # 100 requêtes/minute par IP
