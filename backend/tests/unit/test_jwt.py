"""Unit tests for JWT authentication."""

import pytest
from datetime import timedelta
from unittest.mock import patch
from freezegun import freeze_time


# Import JWT module and functions
from app.core.security.jwt import (
    create_token,
    decode_token,
    create_access_token,
    create_refresh_token,
    create_password_reset_token,
    JWTExpiredSignatureError,
    JWTInvalidTokenError,
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
    TOKEN_TYPE_RESET,
)
from app.core.config import settings

# Test data
TEST_USER_ID = 123
TEST_EMAIL = "test@example.com"


@pytest.fixture(autouse=True)
def setup_jwt_for_tests(monkeypatch):
    """Set up JWT configuration for tests."""

    # Save original values
    original_values = {
        "JWT_SECRET_KEY": settings.JWT_SECRET_KEY,
        "JWT_REFRESH_SECRET_KEY": settings.JWT_REFRESH_SECRET_KEY,
        "JWT_ALGORITHM": settings.JWT_ALGORITHM,
        "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        "JWT_REFRESH_TOKEN_EXPIRE_MINUTES": settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES,
        "JWT_ISSUER": getattr(settings, "JWT_ISSUER", None),
        "JWT_AUDIENCE": getattr(settings, "JWT_AUDIENCE", None),
        "JWT_TOKEN_PREFIX": getattr(settings, "JWT_TOKEN_PREFIX", "Bearer"),
    }

    # Set secure test values with proper encoding
    test_secret_key = "test_secret_key_that_is_long_enough_for_hs256_algorithm_1234567890"
    test_refresh_key = "test_refresh_secret_key_that_is_long_enough_for_hs256_algorithm_1234567890"

    # Update settings with test values
    monkeypatch.setattr(settings, "JWT_SECRET_KEY", test_secret_key)
    monkeypatch.setattr(settings, "JWT_REFRESH_SECRET_KEY", test_refresh_key)
    monkeypatch.setattr(settings, "JWT_ALGORITHM", "HS256")
    monkeypatch.setattr(settings, "JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    monkeypatch.setattr(settings, "JWT_REFRESH_TOKEN_EXPIRE_MINUTES", 10080)  # 7 days in minutes
    monkeypatch.setattr(settings, "JWT_ISSUER", "test_issuer")
    monkeypatch.setattr(settings, "JWT_AUDIENCE", "test_audience")
    monkeypatch.setattr(settings, "JWT_TOKEN_PREFIX", "Bearer")

    # Log the configuration
    print("\n=== JWT Test Configuration ===")
    print(f"JWT_SECRET_KEY: {settings.JWT_SECRET_KEY}")
    print(f"JWT_SECRET_KEY type: {type(settings.JWT_SECRET_KEY).__name__}")
    print(f"JWT_REFRESH_SECRET_KEY: {settings.JWT_REFRESH_SECRET_KEY}")
    print(f"JWT_REFRESH_SECRET_KEY type: {type(settings.JWT_REFRESH_SECRET_KEY).__name__}")
    print(f"JWT_ALGORITHM: {settings.JWT_ALGORITHM}")
    print(f"JWT_ACCESS_TOKEN_EXPIRE_MINUTES: {settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES}")
    print(f"JWT_REFRESH_TOKEN_EXPIRE_MINUTES: {settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES}")
    print(f"JWT_ISSUER: {settings.JWT_ISSUER}")
    print(f"JWT_AUDIENCE: {settings.JWT_AUDIENCE}")
    print(f"JWT_TOKEN_PREFIX: {settings.JWT_TOKEN_PREFIX}")
    print("============================\n")

    try:
        yield settings
    finally:
        # Restore original values
        for key, value in original_values.items():
            setattr(settings, key, value)

    """Test creating a JWT token."""
    # Create a token with a custom claim
    # Vérifier que les clés secrètes ne sont pas vides
    if not settings.JWT_SECRET_KEY:
        print("ERREUR: JWT_SECRET_KEY est vide!")
    if not settings.JWT_REFRESH_SECRET_KEY:
        print("ERREUR: JWT_REFRESH_SECRET_KEY est vide!")

    # Vérifier que les algorithmes sont valides
    from jose import jwt as jose_jwt

    print("\n=== Algorithmes supportés ===")
    print(f"HMAC: {jose_jwt.ALGORITHMS.HMAC}")
    print(f"RSA: {jose_jwt.ALGORITHMS.RSA}")
    print(f"EC: {jose_jwt.ALGORITHMS.EC}")
    print(f"AES: {jose_jwt.ALGORITHMS.AES}")

    # Test with default parameters
    print("\n=== Tentative de création du token ===")
    try:
        print("Avant l'appel à create_token...")
        token = create_token(subject=TEST_USER_ID, token_type=TOKEN_TYPE_ACCESS, expires_delta=timedelta(minutes=30))
        print(f"Token créé avec succès: {token[:50]}...")
    except Exception as e:
        import traceback
        import sys

        print(f"ERREUR lors de la création du token: {e}", file=sys.stderr)
        print(f"Type d'erreur: {type(e).__name__}", file=sys.stderr)
        print("Stack trace:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

        # Afficher plus d'informations sur l'exception
        if hasattr(e, "args") and e.args:
            print("\nArguments de l'exception:", file=sys.stderr)
            for i, arg in enumerate(e.args):
                print(f"  Arg {i}: {arg} (type: {type(arg).__name__})", file=sys.stderr)

        # Vérifier si c'est une erreur liée à la clé secrète
        if "secret" in str(e).lower() or "key" in str(e).lower():
            print("\nERREUR: Problème potentiel avec la clé secrète JWT", file=sys.stderr)

        raise
    assert isinstance(token, str)
    assert len(token.split(".")) == 3  # JWT token has 3 parts

    # Test with custom expiration
    expires_delta = timedelta(minutes=15)
    token = create_token(subject=TEST_USER_ID, token_type=TOKEN_TYPE_ACCESS, expires_delta=expires_delta)
    assert isinstance(token, str)


def test_decode_valid_token():
    """Test decoding a valid JWT token."""
    with freeze_time("2023-01-01 12:00:00"):
        # Create a token with a long expiration
        token = create_token(
            subject=TEST_USER_ID,
            token_type=TOKEN_TYPE_ACCESS,
            custom_claim="test",
            expires_delta=timedelta(days=1),  # Long expiration for testing
        )

        # Decode the token
        payload = decode_token(token)

        # Verify the payload
        assert payload["sub"] == str(TEST_USER_ID)
        assert payload["type"] == TOKEN_TYPE_ACCESS
        assert payload["custom_claim"] == "test"
        assert "exp" in payload
        assert "iat" in payload
    assert "jti" in payload


def test_decode_expired_token():
    """Test decoding an expired JWT token."""
    with freeze_time("2023-01-01 12:00:00") as frozen_datetime:
        # Create a token that expires in 1 second
        token = create_token(
            subject=TEST_USER_ID,
            token_type=TOKEN_TYPE_ACCESS,
            expires_delta=timedelta(seconds=1),  # Very short expiration
        )

        # Move time forward by 2 seconds
        frozen_datetime.tick(delta=timedelta(seconds=2))

        # Should raise expired token error
        with pytest.raises(JWTExpiredSignatureError):
            decode_token(token)


def test_decode_invalid_token():
    """Test decoding an invalid JWT token."""
    with pytest.raises(JWTInvalidTokenError):
        # This is an invalid JWT token
        decode_token("invalid.token.here")


def test_create_access_token():
    """Test creating an access token."""
    with freeze_time("2023-01-01 12:00:00"):
        # Create token with custom data
        token = create_access_token(
            subject=TEST_USER_ID, custom_data={"role": "admin"}, expires_delta=timedelta(minutes=30)
        )

        # Decode and verify
        payload = decode_token(token)
        assert payload["type"] == TOKEN_TYPE_ACCESS
        assert payload["custom_data"]["role"] == "admin"
        assert "exp" in payload
    assert "jti" in payload


def test_create_refresh_token():
    """Test creating a refresh token."""
    with freeze_time("2023-01-01 12:00:00"):
        # Create refresh token with custom data
        custom_data = {"session_id": "test_session_123"}
        token = create_refresh_token(subject=TEST_USER_ID, custom_data=custom_data, expires_delta=timedelta(days=7))

        # Decode and verify
        payload = decode_token(token, token_type=TOKEN_TYPE_REFRESH)
        assert payload["type"] == TOKEN_TYPE_REFRESH
        assert payload["sub"] == str(TEST_USER_ID)
        assert payload["custom_data"] == custom_data
        assert "exp" in payload
        assert "jti" in payload

        # Verify it's not accepted as an access token
        with pytest.raises(JWTInvalidTokenError):
            decode_token(token, token_type=TOKEN_TYPE_ACCESS)


def test_token_with_issuer_and_audience():
    """Test token creation and validation with issuer and audience."""
    with freeze_time("2023-01-01 12:00:00"):
        # Set up test issuer and audience
        test_issuer = "test-issuer"
        test_audience = "test-audience"

        with patch("app.core.security.jwt.settings") as mock_settings:
            # Configurer correctement les paramètres JWT
            mock_settings.JWT_ISSUER = test_issuer
            mock_settings.JWT_AUDIENCE = test_audience
            mock_settings.JWT_ALGORITHM = "HS256"
            mock_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
            mock_settings.JWT_SECRET_KEY = "test_secret_key_that_is_long_enough_for_hs256"
            mock_settings.JWT_REFRESH_SECRET_KEY = "test_refresh_secret_key_that_is_long_enough"

            # Create token with issuer and audience
            token = create_token(
                subject=TEST_USER_ID, token_type=TOKEN_TYPE_ACCESS, expires_delta=timedelta(minutes=30)
            )

            # Decode with correct issuer and audience
            payload = decode_token(token, token_type=TOKEN_TYPE_ACCESS)
            assert payload["iss"] == test_issuer
            assert payload["aud"] == test_audience

            # Test with wrong audience
            with patch("app.core.security.jwt.settings.JWT_AUDIENCE", "wrong-audience"):
                with pytest.raises(JWTInvalidTokenError):
                    decode_token(token, token_type=TOKEN_TYPE_ACCESS)


def test_key_rotation_handling():
    """Test that key rotation is handled correctly."""
    # This test is no longer needed as we're not using key rotation with a key manager
    # The functionality is now handled by the JWT_SECRET_KEY setting
    pass


def test_password_reset_token():
    """Test creating and validating a password reset token."""
    with freeze_time("2023-01-01 12:00:00"):
        token = create_password_reset_token(email=TEST_EMAIL)
        payload = decode_token(token, token_type=TOKEN_TYPE_RESET)

        assert payload["type"] == TOKEN_TYPE_RESET
        assert payload["sub"] == TEST_EMAIL
        assert "exp" in payload

        # Should not accept as access token
        with pytest.raises(JWTInvalidTokenError):
            decode_token(token, token_type=TOKEN_TYPE_ACCESS)
