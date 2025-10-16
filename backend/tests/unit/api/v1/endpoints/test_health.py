"""
Tests unitaires pour app/api/api_v1/endpoints/health.py
"""
import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.api_v1.endpoints.health import router


@pytest.fixture
def test_app():
    """Application de test."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(test_app):
    """Client de test."""
    return TestClient(test_app)


class TestHealthEndpoint:
    """Tests pour l'endpoint /health."""

    def test_health_check_structure(self, client):
        """Test structure de la réponse health check."""
        # Mock DB dependency
        async def mock_db():
            mock_session = AsyncMock(spec=AsyncSession)
            mock_session.execute = AsyncMock(return_value=None)
            yield mock_session
        
        with patch('app.api.api_v1.endpoints.health.get_async_db', mock_db):
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            
            # Vérifie structure
            assert "status" in data
            assert "database" in data
            assert "version" in data
            assert data["version"] == "1.0.0"

    def test_health_check_db_success(self, client):
        """Test health check avec DB OK."""
        async def mock_db():
            mock_session = AsyncMock(spec=AsyncSession)
            mock_session.execute = AsyncMock(return_value=None)
            yield mock_session
        
        with patch('app.api.api_v1.endpoints.health.get_async_db', mock_db):
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert data["database"] == "ok"

