"""Debug test to verify auth_headers fixture works correctly."""

import pytest
from httpx import AsyncClient
from app.core.config import settings


@pytest.mark.asyncio
async def test_auth_headers_debug(async_client: AsyncClient, auth_headers, db_session):
    """Debug test to verify auth headers work."""
    from sqlalchemy import select, text
    from app.models.user import User
    
    # Create a superuser
    headers = await auth_headers(username="debug_admin", is_superuser=True)
    
    print(f"\n=== DEBUG INFO ===")
    print(f"Headers: {headers}")
    print(f"Token: {headers.get('Authorization', 'NO TOKEN')}")
    
    # Check if user exists in DB
    result = await db_session.execute(select(User).where(User.id == 1))
    user = result.scalar_one_or_none()
    print(f"User in DB: {user}")
    if user:
        print(f"User details: id={user.id}, email={user.email}, is_superuser={user.is_superuser}, is_active={user.is_active}")
    
    # Check all users
    result = await db_session.execute(text("SELECT id, email, username, is_superuser, is_active FROM user"))
    all_users = result.fetchall()
    print(f"All users in DB: {all_users}")
    
    # Try to access a protected endpoint
    response = await async_client.get(
        f"{settings.API_V1_STR}/users/me",
        headers=headers
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # This should work if auth is configured correctly
    assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}: {response.text}"
