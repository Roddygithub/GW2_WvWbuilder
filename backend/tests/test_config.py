"""Test configuration for the application."""
from pathlib import Path
from typing import Any, Dict

from pydantic import AnyHttpUrl, PostgresDsn, validator
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    """Test settings for the application."""
    
    # Application settings
    PROJECT_NAME: str = "GW2 WvW Builder API - Test"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "test-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    SERVER_NAME: str = "testserver"
    SERVER_HOST: AnyHttpUrl = "http://testserver"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "test_db"
    SQLALCHEMY_DATABASE_URI: str | None = None
    
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: str | None, values: Dict[str, Any]) -> str:
        if isinstance(v, str):
            return v
        return "sqlite+aiosqlite:///:memory:"
    
    # Test settings
    TESTING: bool = True
    TEST_DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"
    
    # Security settings
    FIRST_SUPERUSER: str = "test@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "testpassword"
    
    class Config:
        case_sensitive = True
        env_file = ".env.test"


# Create an instance of the test settings
test_settings = TestSettings()
