"""Debug test to verify auth_headers fixture works correctly."""

import pytest
from httpx import AsyncClient
from app.core.config import settings


@pytest.mark.asyncio
async def test_auth_headers_debug(async_client: AsyncClient, auth_headers, db_session):
    """Debug test to verify auth headers work."""
    from sqlalchemy import select, text
    from app.models.user import User
    from app.core.config import settings as app_settings
    
    # Verify JWT keys are synchronized
    print(f"\n=== JWT KEYS CHECK ===")
    print(f"settings.JWT_SECRET_KEY: {app_settings.JWT_SECRET_KEY}")
    print(f"settings.SECRET_KEY: {app_settings.SECRET_KEY}")
    
    # Create a superuser
    headers = await auth_headers(username="debug_admin", is_superuser=True)
    
    print(f"\n=== DEBUG INFO ===")
    print(f"Headers: {headers}")
    token_str = headers.get('Authorization', '').replace('Bearer ', '')
    print(f"Token: {token_str}")
    
    # Decode token to see payload
    from jose import jwt
    import time
    try:
        # Decode without verification first to see payload
        payload_unverified = jwt.decode(token_str, options={"verify_signature": False, "verify_exp": False})
        print(f"Token payload (unverified): {payload_unverified}")
        print(f"Token exp: {payload_unverified.get('exp')}, current time: {int(time.time())}")
        print(f"Time until expiry: {payload_unverified.get('exp', 0) - int(time.time())} seconds")
        
        # Now try with verification
        payload = jwt.decode(token_str, app_settings.SECRET_KEY, algorithms=[app_settings.JWT_ALGORITHM])
        print(f"Token payload (verified): {payload}")
    except Exception as e:
        print(f"Token decode error: {e}")
    
    # Check if user exists in DB
    result = await db_session.execute(select(User).where(User.id == 1))
    user = result.scalar_one_or_none()
    print(f"User in DB: {user}")
    if user:
        print(f"User details: id={user.id}, email={user.email}, is_superuser={user.is_superuser}, is_active={user.is_active}")
    
    # Check all users (table name is "users" plural)
    result = await db_session.execute(text("SELECT id, email, username, is_superuser, is_active FROM users"))
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
