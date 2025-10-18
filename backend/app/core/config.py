import os
from typing import Optional, Any, cast
from pydantic_settings import BaseSettings
import redis.asyncio as redis
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()


class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    TESTING: bool = os.getenv("TESTING", "False").lower() == "true"

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GW2 WvW Builder API"
    VERSION: str = os.getenv("VERSION", "1.0.0")
    API_VERSION: str = os.getenv(
        "API_VERSION", "1.0.0"
    )  # Pour la compatibilité avec les tests
    SERVER_NAME: str = os.getenv("SERVER_NAME", "localhost")
    SERVER_HOST: str = os.getenv("SERVER_HOST", "http://localhost:8000")

    # CORS Configuration
    @property
    def BACKEND_CORS_ORIGINS(self) -> list[str]:
        """Parse CORS origins from environment variable."""
        cors_str = os.getenv(
            "BACKEND_CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000",
        )
        return [origin.strip() for origin in cors_str.split(",") if origin.strip()]

    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "supersecretjwtkey")
    JWT_REFRESH_SECRET_KEY: str = os.getenv(
        "JWT_REFRESH_SECRET_KEY", "supersecretrefreshkey"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("JWT_REFRESH_TOKEN_EXPIRE_MINUTES", "1440")
    )
    JWT_TOKEN_PREFIX: str = os.getenv("JWT_TOKEN_PREFIX", "Bearer")
    JWT_ISSUER: str = os.getenv("JWT_ISSUER", "gw2-wvwbuilder-api")
    JWT_AUDIENCE: str = os.getenv("JWT_AUDIENCE", "gw2-wvwbuilder-client")

    # For backward compatibility
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("JWT_REFRESH_TOKEN_EXPIRE_MINUTES", "1440")
    )

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkeyfordevelopmentonly")
    SECRET_KEY_ROTATION_INTERVAL_DAYS: int = int(
        os.getenv("SECRET_KEY_ROTATION_INTERVAL_DAYS", "90")
    )
    MAX_OLD_KEYS: int = int(os.getenv("MAX_OLD_KEYS", "3"))

    # Database
    DATABASE_TYPE: str = "sqlite"
    DATABASE_NAME: str = "gw2_wvwbuilder"
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./gw2_wvwbuilder.db"
    ASYNC_SQLALCHEMY_DATABASE_URI: str = "sqlite+aiosqlite:///./gw2_wvwbuilder.db"

    # Database connection pool settings
    POOL_SIZE: int = 5
    MAX_OVERFLOW: int = 10
    POOL_RECYCLE: int = 3600
    POOL_TIMEOUT: int = 30
    SQL_ECHO: bool = False
    SQL_ECHO_POOL: bool = False

    # GW2 API Configuration
    GW2_API_BASE_URL: str = "https://api.guildwars2.com/v2"
    GW2_WIKI_API_URL: str = "https://wiki.guildwars2.com/api.php"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_TO_FILE: bool = False
    LOG_FILE: str = "app.log"

    # Cache
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"

    # Désactiver le cache en environnement de test
    if ENVIRONMENT == "test" or TESTING:
        CACHE_ENABLED = False
        REDIS_URL = ""  # Désactive la connexion Redis

    # Database URLs for testing
    DATABASE_URL: Optional[str] = None
    TEST_DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"

    # Redis client for rate limiting
    @property
    def redis_client(self) -> Any:
        if not self.REDIS_URL:
            # Retourne un client factice si REDIS_URL est vide (pour les tests)
            class MockRedis:
                async def get(self, *args: Any, **kwargs: Any) -> Any:
                    return None

                async def set(self, *args: Any, **kwargs: Any) -> bool:
                    return True

                async def close(self, *args: Any, **kwargs: Any) -> None:
                    pass

            return MockRedis()
        return cast(
            Any, redis.from_url(self.REDIS_URL, encoding="utf-8", decode_responses=True)
        )

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields in .env files

    def get_database_url(self) -> str:
        """Get the synchronous database URL, using test override if provided."""
        return self.DATABASE_URL or self.SQLALCHEMY_DATABASE_URI

    def get_async_test_database_url(self) -> str:
        """Get the async database URL for testing."""
        if self.TESTING:
            return "sqlite+aiosqlite:///file:testdb?mode=memory&cache=shared"  # Base de données en mémoire partagée
        return self.ASYNC_SQLALCHEMY_DATABASE_URI

    def get_async_database_url(self) -> str:
        """Get the asynchronous database URL, converting from sync URL if needed."""
        if self.TESTING:
            # Pour les tests, utiliser une base de données en mémoire partagée
            return "sqlite+aiosqlite:///file:testdb?mode=memory&cache=shared&uri=true"

        if self.DATABASE_URL:
            # Convert sync URL to async URL if needed
            if self.DATABASE_URL.startswith("sqlite"):
                # Pour SQLite, on utilise aiosqlite comme pilote asynchrone
                if "+aiosqlite" not in self.DATABASE_URL:
                    return self.DATABASE_URL.replace("sqlite", "sqlite+aiosqlite", 1)
                return self.DATABASE_URL
            elif self.DATABASE_URL.startswith("postgresql"):
                if "+asyncpg" not in self.DATABASE_URL:
                    return self.DATABASE_URL.replace(
                        "postgresql", "postgresql+asyncpg", 1
                    )
                return self.DATABASE_URL
            elif self.DATABASE_URL.startswith("mysql"):
                if "+asyncmy" not in self.DATABASE_URL:
                    return self.DATABASE_URL.replace("mysql", "mysql+asyncmy", 1)
                return self.DATABASE_URL
            return self.DATABASE_URL

        # Si aucune URL spécifique n'est fournie, utiliser l'URL asynchrone par défaut
        if not self.ASYNC_SQLALCHEMY_DATABASE_URI.startswith(
            "sqlite+aiosqlite"
        ) and self.ASYNC_SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
            return self.ASYNC_SQLALCHEMY_DATABASE_URI.replace(
                "sqlite", "sqlite+aiosqlite", 1
            )

        return self.ASYNC_SQLALCHEMY_DATABASE_URI


# Create settings instance
settings = Settings()


def validate_secret_keys() -> None:
    """
    Validate that secret keys are properly configured and secure.

    Raises:
        ValueError: If keys are not set or are using default/weak values in production
    """
    if settings.ENVIRONMENT == "production":
        # Check SECRET_KEY
        if (
            not settings.SECRET_KEY
            or settings.SECRET_KEY == "supersecretkeyfordevelopmentonly"
        ):
            raise ValueError(
                "SECRET_KEY must be set to a strong value in production. "
                "Generate one with: openssl rand -hex 32"
            )

        # Check JWT_SECRET_KEY
        if (
            not settings.JWT_SECRET_KEY
            or settings.JWT_SECRET_KEY == "supersecretjwtkey"
        ):
            raise ValueError(
                "JWT_SECRET_KEY must be set to a strong value in production. "
                "Generate one with: openssl rand -hex 32"
            )

        # Check JWT_REFRESH_SECRET_KEY
        if (
            not settings.JWT_REFRESH_SECRET_KEY
            or settings.JWT_REFRESH_SECRET_KEY == "supersecretrefreshkey"
        ):
            raise ValueError(
                "JWT_REFRESH_SECRET_KEY must be set to a strong value in production. "
                "Generate one with: openssl rand -hex 32"
            )

        # Check minimum key length (64 hex chars = 32 bytes)
        if len(settings.SECRET_KEY) < 64:
            raise ValueError(
                "SECRET_KEY must be at least 64 characters long (32 bytes in hex)"
            )

        if len(settings.JWT_SECRET_KEY) < 64:
            raise ValueError(
                "JWT_SECRET_KEY must be at least 64 characters long (32 bytes in hex)"
            )

        if len(settings.JWT_REFRESH_SECRET_KEY) < 64:
            raise ValueError(
                "JWT_REFRESH_SECRET_KEY must be at least 64 characters long (32 bytes in hex)"
            )


def get_settings() -> Settings:
    """
    Get the settings instance.

    This function is used for dependency injection in FastAPI routes.
    """
    return settings
