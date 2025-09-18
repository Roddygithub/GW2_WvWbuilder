"""Unit tests for security utilities."""
import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from app.core.config import settings
from fastapi import HTTPException
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_active_user,
    get_current_active_superuser
)

def test_password_hashing():
    """Test password hashing and verification."""
    # Test with a simple password
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    # Verify the hash is not the same as the password
    assert hashed != password
    
    # Verify the password can be verified
    assert verify_password(password, hashed) is True
    
    # Test with a different password
    assert verify_password("wrongpassword", hashed) is False
    
    # Test with an empty password
    empty_hash = get_password_hash("")
    assert verify_password("", empty_hash) is True
    assert verify_password(" ", empty_hash) is False

def test_jwt_token_creation():
    """Test JWT token creation."""
    # Test token creation with user ID
    user_id = 1
    token = create_access_token(subject=user_id)
    
    # Verify token structure
    assert isinstance(token, str)
    assert len(token.split('.')) == 3  # JWT has 3 parts
    
    # Decode the token to verify its contents
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
        options={"verify_aud": False}
    )
    
    # Verify the payload contains the expected fields
    assert "sub" in payload
    assert payload["sub"] == str(user_id)
    assert "exp" in payload
    
    # Test token expiration
    expiration_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    assert expiration_time > datetime.now(timezone.utc)

def test_token_verification():
    """Test token verification."""
    # Create a valid token
    user_id = 1
    token = create_access_token(subject=user_id)
    
    # Verify the token can be decoded with the correct secret
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
        options={"verify_aud": False}
    )
    assert payload["sub"] == str(user_id)
    
    # Test with invalid token
    with pytest.raises(JWTError):
        jwt.decode(
            "invalid.token.here",
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False}
        )
    
    # Test with expired token
    with pytest.raises(JWTError):
        expired_token = jwt.encode(
            {"sub": user_id, "exp": datetime.utcnow() - timedelta(seconds=1)},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        jwt.decode(
            expired_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False}
        )

def test_user_authentication_flow():
    """Test the complete user authentication flow."""
    # This is a placeholder for testing the actual authentication flow
    # which would require a test database and proper user setup
    # The actual implementation would test:
    # 1. User registration
    # 2. Password hashing and verification
    # 3. Token creation and verification
    # 4. Protected route access with tokens
    pass

def test_user_authorization():
    """Test user authorization."""
    # This would test the get_current_user and related functions
    # Requires mocking the database and authentication
    pass

def test_admin_authorization():
    """Test admin authorization."""
    # This would test the get_current_active_superuser function
    # Requires mocking the database and authentication
    pass

def test_token_blacklist():
    """Test token blacklisting functionality (placeholder)."""
    # This would test token blacklisting functionality
    # Requires Redis and proper test setup
    pass

def test_password_strength_verification():
    """Test password strength verification."""
    # This would test password strength verification
    # The actual implementation would test various password strengths
    pass

def test_generate_secure_random():
    """Test generation of secure random strings."""
    # This would test secure random string generation
    # The actual implementation would test the generation of random strings
    pass
