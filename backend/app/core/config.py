from pydantic_settings import BaseSettings
from typing import List, Optional, Union


class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    TESTING: bool = False

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GW2 WvW Builder API"
    SERVER_NAME: str = "localhost"
    SERVER_HOST: str = "http://localhost:8000"

    # Security
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"  # Algorithm for JWT

    # CORS
    BACKEND_CORS_ORIGINS: List[Union[str, dict]] = ["*"]

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
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 300  # 5 minutes
    CACHE_ENABLED: bool = True
    
    # Optional override used by tests
    DATABASE_URL: Optional[str] = None

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields in .env files

    def get_database_url(self) -> str:
        """Get the synchronous database URL, using test override if provided."""
        return self.DATABASE_URL or self.SQLALCHEMY_DATABASE_URI

    def get_async_database_url(self) -> str:
        """Get the asynchronous database URL, converting from sync URL if needed."""
        if self.DATABASE_URL:
            # Convert sync URL to async URL if needed
            if self.DATABASE_URL.startswith("sqlite"):
                return self.DATABASE_URL.replace("sqlite", "sqlite+aiosqlite", 1)
            elif self.DATABASE_URL.startswith("postgresql"):
                return self.DATABASE_URL.replace("postgresql", "postgresql+asyncpg", 1)
            elif self.DATABASE_URL.startswith("mysql"):
                return self.DATABASE_URL.replace("mysql", "mysql+asyncmy", 1)
            return self.DATABASE_URL
        return self.ASYNC_SQLALCHEMY_DATABASE_URI


# Create settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get the settings instance.
    
    This function is used for dependency injection in FastAPI routes.
    """
    return settings
