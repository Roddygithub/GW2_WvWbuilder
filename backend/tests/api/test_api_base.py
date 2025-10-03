"""
Tests de base pour les endpoints d'API.

Ces tests vérifient les fonctionnalités de base de l'application,
comme l'état de santé et la disponibilité de la documentation.
"""

import pytest
import time
from fastapi import status
from httpx import AsyncClient

from app.core.config import settings


@pytest.mark.asyncio
class TestAPIBase:
    """Tests de base pour les endpoints d'API."""

    async def test_health_check(self, async_client: AsyncClient):
        """Teste l'endpoint de vérification de santé de l'API."""
        response = await async_client.get(f"{settings.API_V1_STR}/health")
        assert response.status_code == status.HTTP_200_OK, \
            f"Expected status code 200, got {response.status_code}. Response: {response.text}"
        data = response.json()
        assert data["status"] == "ok", f"Expected status 'ok', got '{data['status']}'"
        assert data["database"] == "ok", f"Expected database status 'ok', got '{data['database']}'"

    async def test_docs_available(self, async_client: AsyncClient):
        """Vérifie que la documentation de l'API (Swagger UI) est disponible."""
        response = await async_client.get("/docs")
        assert response.status_code == status.HTTP_200_OK, \
            f"Expected status code 200 for /docs, got {response.status_code}. Response: {response.text}"
        assert "text/html" in response.headers["content-type"], \
            f"Expected 'text/html' content type, got '{response.headers['content-type']}'"

    async def test_openapi_schema_available(self, async_client: AsyncClient):
        """Vérifie que le schéma OpenAPI est disponible."""
        response = await async_client.get(f"{settings.API_V1_STR}/openapi.json")
        assert response.status_code == status.HTTP_200_OK, \
            f"Expected status code 200 for /openapi.json, got {response.status_code}. Response: {response.text}"
        data = response.json()
        assert "openapi" in data, "OpenAPI schema should contain 'openapi' field"
        assert "info" in data, "OpenAPI schema should contain 'info' field"
        assert "version" in data["info"], "OpenAPI schema info should contain 'version' field"

    async def test_api_version_in_health_check(self, async_client: AsyncClient):
        """Vérifie que l'endpoint de santé retourne la version de l'API."""
        response = await async_client.get(f"{settings.API_V1_STR}/health")
        assert response.status_code == status.HTTP_200_OK, \
            f"Expected status code 200, got {response.status_code}. Response: {response.text}"
        data = response.json()
        assert "version" in data, "Health check response should contain 'version' field"
        assert data["version"] == "1.0.0", f"Expected API version '1.0.0', got '{data['version']}'"

    @pytest.mark.performance
    async def test_health_check_performance(self, async_client: AsyncClient):
        """Vérifie que l'endpoint de santé répond rapidement."""
        start_time = time.time()
        response = await async_client.get(f"{settings.API_V1_STR}/health")
        elapsed = time.time() - start_time
        assert response.status_code == status.HTTP_200_OK
        assert elapsed < 1.0, f"Health check took too long: {elapsed:.2f}s"

    async def test_security_headers(self, async_client: AsyncClient):
        """Vérifie la présence des en-têtes de sécurité de base."""
        response = await async_client.get(f"{settings.API_V1_STR}/health")
        security_headers = {
            "x-content-type-options": "nosniff",
            "x-frame-options": "DENY",
        }
        for header, expected_value in security_headers.items():
            assert header in response.headers, f"Missing security header: {header}"
            assert response.headers[header] == expected_value, \
                f"Invalid value for {header}: got '{response.headers[header]}', expected '{expected_value}'"

    @pytest.mark.parametrize("endpoint", [
        f"{settings.API_V1_STR}/health",
        "/docs",
        f"{settings.API_V1_STR}/openapi.json"
    ])
    async def test_invalid_methods_on_get_endpoints(self, async_client: AsyncClient, endpoint: str):
        """Teste que les méthodes non autorisées (POST, PUT, DELETE) sont rejetées sur les endpoints GET."""
        for method in ["POST", "PUT", "DELETE", "PATCH"]:
            response = await async_client.request(method, endpoint)
            assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED, \
                f"Expected 405 for {method} {endpoint}, got {response.status_code}"