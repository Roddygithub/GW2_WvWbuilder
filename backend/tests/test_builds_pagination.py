"""Test builds pagination validation."""

import pytest
from fastapi import status
from httpx import AsyncClient
from app.core.config import settings

pytestmark = pytest.mark.asyncio


async def test_list_builds_with_invalid_pagination(client: AsyncClient, auth_headers):
    """Test listing builds with invalid pagination parameters."""
    # Get auth headers with a test user
    headers = await auth_headers()

    # Test with negative skip
    response = await client.get(
        f"{settings.API_V1_STR}/builds/",
        params={"skip": -1},
        headers=headers,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test with zero limit
    response = await client.get(
        f"{settings.API_V1_STR}/builds/",
        params={"limit": 0},
        headers=headers,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test with non-integer values
    response = await client.get(
        f"{settings.API_V1_STR}/builds/",
        params={"skip": "not_an_integer", "limit": "also_not_an_integer"},
        headers=headers,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
