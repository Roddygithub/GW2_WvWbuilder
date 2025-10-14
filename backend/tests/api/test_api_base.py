"""
Tests de base pour les endpoints d'API.

Ces tests vérifient les fonctionnalités de base de l'application,
comme l'état de santé et la disponibilité de la documentation.
"""

import pytest
import time
from fastapi import status

from app.core.config import settings


@pytest.mark.asyncio
class TestAPIBase:
    async def test_health_check(self, async_client):
        """Teste l'endpoint de vérification de santé de l'API."""
        response = await async_client.get(f"{settings.API_V1_STR}/health")
        assert (
            response.status_code == status.HTTP_200_OK
        ), f"Expected status code 200, got {response.status_code}. Response: {response.text}"
        data = response.json()
        assert data.get("status") == "ok", f"Expected status 'ok', got '{data.get('status')}'"
        assert data.get("database") == "ok", f"Expected database status 'ok', got '{data.get('database')}'"

    async def test_docs_available(self, async_client):
        """Vérifie que la documentation de l'API (Swagger UI) est disponible."""
        response = await async_client.get("/docs")
        assert (
            response.status_code == status.HTTP_200_OK
        ), f"La documentation de l'API n'est pas disponible. Statut: {response.status_code}. Response: {response.text}"
        assert "text/html" in response.headers.get(
            "content-type", ""
        ), f"Expected 'text/html' content type, got '{response.headers.get('content-type')}'"

    async def test_openapi_schema_available(self, async_client):
        """Vérifie que le schéma OpenAPI est disponible."""
        response = await async_client.get(f"{settings.API_V1_STR}/openapi.json")
        assert (
            response.status_code == status.HTTP_200_OK
        ), f"Expected status code 200 for /openapi.json, got {response.status_code}. Response: {response.text}"
        data = response.json()
        assert "openapi" in data, "OpenAPI schema should contain 'openapi' field"
        assert "info" in data, "OpenAPI schema should contain 'info' field"
        assert "version" in data.get("info", {}), "OpenAPI schema info should contain 'version' field"

    async def test_api_version_in_health_check(self, async_client):
        """Vérifie que l'endpoint de santé retourne la version de l'API."""
        response = await async_client.get(f"{settings.API_V1_STR}/health")
        assert response.status_code == status.HTTP_200_OK, f"Expected status code 200, got {response.status_code}"
        data = response.json()
        assert "version" in data, "Health check response should contain 'version' field"
        assert (
            data.get("version") == settings.API_VERSION
        ), f"Expected API version {settings.API_VERSION}, got {data.get('version')}"

    @pytest.mark.performance
    async def test_health_check_performance(self, async_client):
        """Vérifie que l'endpoint de santé répond rapidement."""
        start_time = time.time()
        response = await async_client.get(f"{settings.API_V1_STR}/health")
        assert response.status_code == status.HTTP_200_OK, f"Expected status code 200, got {response.status_code}"
        end_time = time.time()
        response_time = end_time - start_time
        assert response_time < 1.0, f"Health check took {response_time:.2f} seconds, expected < 1.0 second"

    async def test_security_headers(self, async_client):
        """Vérifie la présence des en-têtes de sécurité de base."""
        response = await async_client.get(f"{settings.API_V1_STR}/health")
        headers = response.headers
        security_headers = ["X-Content-Type-Options", "X-Frame-Options", "X-XSS-Protection", "Content-Security-Policy"]
        for header in security_headers:
            assert header in headers, f"Missing {header} header"

    @pytest.mark.parametrize(
        "endpoint,methods",
        [
            (f"{settings.API_V1_STR}/health", ["POST", "PUT", "DELETE"]),
            ("/docs", ["POST", "PUT", "DELETE"]),
            (f"{settings.API_V1_STR}/openapi.json", ["POST", "PUT", "DELETE"]),
        ],
    )
    async def test_invalid_methods_on_get_endpoints(self, async_client, endpoint: str, methods: list):
        """Teste que les méthodes non autorisées (POST, PUT, DELETE) sont rejetées sur les endpoints GET."""
        for method in methods:
            response = await async_client.request(method, endpoint)
            assert response.status_code in [
                status.HTTP_405_METHOD_NOT_ALLOWED,
                status.HTTP_404_NOT_FOUND,
            ], f"{method} should not be allowed on {endpoint}"
