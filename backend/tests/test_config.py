"""Test configuration for the application."""

from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    """Test settings for the application."""

    # Environment
    ENVIRONMENT: str = "test"
    DEBUG: bool = True
    TESTING: bool = True

    # Application settings
    PROJECT_NAME: str = "GW2 WvW Builder API - Test"
    API_V1_STR: str = "/api/v1"
    SERVER_NAME: str = "testserver"
    SERVER_HOST: str = "http://testserver"

    # Security settings
    SECRET_KEY: str = "test-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"

    # CORS settings
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    # Database settings
    DATABASE_TYPE: str = "sqlite"
    DATABASE_NAME: str = "test_db"
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    ASYNC_SQLALCHEMY_DATABASE_URI: str = "sqlite+aiosqlite:///:memory:"

    # Database connection pool settings
    POOL_SIZE: int = 5
    MAX_OVERFLOW: int = 10
    POOL_RECYCLE: int = 3600
    POOL_TIMEOUT: int = 30
    SQL_ECHO: bool = False
    SQL_ECHO_POOL: bool = False

    # Logging
    LOG_LEVEL: str = "WARNING"
    LOG_TO_FILE: bool = False
    LOG_FILE: str = "test.log"

    # Test user
    FIRST_SUPERUSER: str = "test@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "testpassword"

    # Optional override used by tests
    DATABASE_URL: str | None = None

    def get_database_url(self) -> str:
        """Get the synchronous database URL, using test override if provided."""
        return self.DATABASE_URL or self.SQLALCHEMY_DATABASE_URI

    def get_async_database_url(self) -> str:
        """Get the asynchronous database URL, converting from sync URL if needed."""
        if self.DATABASE_URL:
            # Convert sync URL to async URL if needed
            if self.DATABASE_URL.startswith("sqlite"):
                return self.DATABASE_URL.replace("sqlite", "sqlite+aiosqlite", 1)
            return self.DATABASE_URL
        return self.ASYNC_SQLALCHEMY_DATABASE_URI

    class Config:
        case_sensitive = True
        env_file = ".env.test"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields in .env files


# Create an instance of the test settings
test_settings = TestSettings()
