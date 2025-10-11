"""Test application configuration settings."""

import os
from unittest.mock import patch

import pytest

from app.core.config import Settings


class TestSettings:
    """Test the application settings."""

    def test_default_settings(self):
        """Test that default settings are loaded correctly."""
        # Create settings with default values
        config = Settings()

        # Test some default values
        assert config.API_V1_STR == "/api/v1"
        assert config.PROJECT_NAME == "GW2 WvW Builder API"
        assert config.DEBUG is True
        assert config.TESTING is False
        assert config.SECRET_KEY == "your-secret-key-here"
        assert config.ACCESS_TOKEN_EXPIRE_MINUTES == 60 * 24 * 8  # 8 days
        assert config.ALGORITHM == "HS256"
        assert config.BACKEND_CORS_ORIGINS == ["*"]
        assert config.SQLALCHEMY_DATABASE_URI == "sqlite:///./gw2_wvwbuilder.db"
        assert config.ASYNC_SQLALCHEMY_DATABASE_URI == "sqlite+aiosqlite:///./gw2_wvwbuilder.db"

    def test_environment_variables(self):
        """Test that environment variables override defaults."""
        with patch.dict(
            os.environ,
            {
                "PROJECT_NAME": "Test Project",
                "DEBUG": "false",
                "SECRET_KEY": "test-secret-key",
                "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
                "BACKEND_CORS_ORIGINS": '["http://test1", "http://test2"]',
            },
        ):
            config = Settings()

            assert config.PROJECT_NAME == "Test Project"
            assert config.DEBUG is False
            assert config.SECRET_KEY == "test-secret-key"
            assert config.ACCESS_TOKEN_EXPIRE_MINUTES == 30
            # Pydantic v2 with SettingsConfigDict uses json.loads for list fields
            assert config.BACKEND_CORS_ORIGINS == ["http://test1", "http://test2"]

    def test_boolean_environment_variables(self):
        """
        Test that boolean environment variables are parsed correctly.

        Test different boolean string representations (case insensitive).
        """
        for value in ("true", "True", "1", "y", "yes"):
            with patch.dict(os.environ, {"DEBUG": value}):
                assert Settings().DEBUG is True

        for value in ("false", "False", "0", "n", "no"):
            with patch.dict(os.environ, {"DEBUG": value}):
                assert Settings().DEBUG is False

    def test_list_environment_variables(self):
        """Test that list environment variables are parsed correctly."""
        # Test with JSON array (Pydantic v2 with SettingsConfigDict requires JSON for list fields)
        with patch.dict(os.environ, {"BACKEND_CORS_ORIGINS": '["http://x", "http://y"]'}):
            config = Settings()
            assert config.BACKEND_CORS_ORIGINS == ["http://x", "http://y"]

        # Test that invalid JSON raises a validation error
        with (
            patch.dict(os.environ, {"BACKEND_CORS_ORIGINS": "not-a-json-array"}),
            pytest.raises(ValueError),
        ):
            Settings()

    def test_get_database_url(self):
        """Test the get_database_url method."""
        # Test with default SQLite URL
        config = Settings()
        assert config.get_database_url() == "sqlite:///./gw2_wvwbuilder.db"

        # Test with custom URL
        config.SQLALCHEMY_DATABASE_URI = "postgresql://user:pass@localhost/db"
        assert config.get_database_url() == "postgresql://user:pass@localhost/db"

    def test_get_async_database_url(self):
        """
        Test the get_async_database_url method.

        Test different database URLs.
        """
        config = Settings()

        # Test with default SQLite URL
        assert config.get_async_database_url() == "sqlite+aiosqlite:///./gw2_wvwbuilder.db"

        # Test with PostgreSQL DATABASE_URL
        config.DATABASE_URL = "postgresql://user:pass@localhost/db"
        assert config.get_async_database_url() == "postgresql+asyncpg://user:pass@localhost/db"

        # Test with MySQL DATABASE_URL
        config.DATABASE_URL = "mysql://user:pass@localhost/db"
        assert config.get_async_database_url() == "mysql+asyncmy://user:pass@localhost/db"

    def test_env_file_loading(self, tmp_path):
        """Test loading settings from environment variables."""
        # Test with environment variables directly
        with patch.dict(
            os.environ,
            {
                "SECRET_KEY": "test-secret-key",
                "DEBUG": "false",
                "ACCESS_TOKEN_EXPIRE_MINUTES": "45",
                "SQLALCHEMY_DATABASE_URI": "sqlite:///test.db",
            },
        ):
            config = Settings()

            # Verify settings from environment variables
            assert config.SECRET_KEY == "test-secret-key"
            assert config.DEBUG is False
            assert config.ACCESS_TOKEN_EXPIRE_MINUTES == 45
            assert config.SQLALCHEMY_DATABASE_URI == "sqlite:///test.db"

    def test_validation_errors(self):
        """Test that validation errors are raised for invalid settings."""
        # Test with invalid boolean
        with pytest.raises(ValueError):
            Settings(DEBUG="not-a-boolean")

        # Test with invalid integer
        with pytest.raises(ValueError):
            Settings(ACCESS_TOKEN_EXPIRE_MINUTES="not-an-integer")

        # Test with invalid list
        with pytest.raises(ValueError):
            Settings(BACKEND_CORS_ORIGINS="not a list")


class TestSettingsSingleton:
    """Test that the settings singleton works correctly."""

    def test_settings_singleton(self):
        """Test that the settings object is a singleton."""
        from app.core.config import settings as settings1
        from app.core.config import settings as settings2

        # Both should be the same object
        assert settings1 is settings2

        # Modifying one should affect the other
        settings1.DEBUG = True
        assert settings2.DEBUG is True

        settings2.DEBUG = False
        assert settings1.DEBUG is False
