"""Tests for application configuration."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings


def test_get_settings():
    """Test that get_settings returns a Settings instance."""
    settings = get_settings()
    assert isinstance(settings, Settings)


def test_settings_defaults():
    """Test default settings values."""
    settings = Settings()
    assert settings.PROJECT_NAME == "GW2 WvW Builder"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.SECRET_KEY is not None
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60 * 24 * 8  # 8 days
    assert settings.USERS_OPEN_REGISTRATION is True


def test_settings_from_env(monkeypatch):
    """Test that settings can be overridden by environment variables."""
    monkeypatch.setenv("PROJECT_NAME", "Test Project")
    monkeypatch.setenv("SECRET_KEY", "test_secret_key")
    monkeypatch.setenv("USERS_OPEN_REGISTRATION", "false")

    settings = Settings()
    assert settings.PROJECT_NAME == "Test Project"
    assert settings.SECRET_KEY == "test_secret_key"
    assert settings.USERS_OPEN_REGISTRATION is False


def test_database_url(monkeypatch):
    """Test database URL construction."""
    # Test with SQLite
    settings = Settings()
    assert settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite+aiosqlite:///")

    # Test with PostgreSQL
    monkeypatch.setenv("POSTGRES_SERVER", "localhost")
    monkeypatch.setenv("POSTGRES_USER", "testuser")
    monkeypatch.setenv("POSTGRES_PASSWORD", "testpass")
    monkeypatch.setenv("POSTGRES_DB", "testdb")

    settings = Settings()
    assert settings.SQLALCHEMY_DATABASE_URI == "postgresql+asyncpg://testuser:testpass@localhost/testdb"


def test_invalid_cors_origins():
    """Test validation of CORS origins."""
    with pytest.raises(ValidationError):
        Settings(BACKEND_CORS_ORIGINS="invalid_url")  # type: ignore

    # Test with valid single URL
    settings = Settings(BACKEND_CORS_ORIGINS="http://localhost:3000")
    assert settings.BACKEND_CORS_ORIGINS == ["http://localhost:3000"]

    # Test with JSON array
    settings = Settings(BACKEND_CORS_ORIGINS='["http://localhost:3000", "https://example.com"]')
    assert settings.BACKEND_CORS_ORIGINS == ["http://localhost:3000", "https://example.com"]


def test_log_level_validation():
    """Test log level validation."""
    with pytest.raises(ValidationError):
        Settings(LOG_LEVEL="INVALID_LEVEL")  # type: ignore

    # Test valid log levels
    for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        settings = Settings(LOG_LEVEL=level)
        assert settings.LOG_LEVEL == level
