"""Additional error tests for Builds API endpoints - Part 2."""

from typing import Dict, Any
import pytest
from fastapi import status
from httpx import AsyncClient

from app.core.config import settings

pytestmark = pytest.mark.asyncio

class TestBuildsErrorHandlingPart2:
    """Additional test error handling for Builds API endpoints."""

    async def test_update_nonexistent_build(
        self, async_client: AsyncClient, test_user: Dict[str, Any]
    ):
        """Test updating a build that doesn't exist."""
        non_existent_id = 999999  # Assuming this ID doesn't exist
        update_data = {
            "name": "Updated Build",
            "game_mode": "wvw",
            "team_size": 5,
        }
        
        response = await async_client.put(
            f"{settings.API_V1_STR}/builds/{non_existent_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {test_user['access_token']}"},
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
