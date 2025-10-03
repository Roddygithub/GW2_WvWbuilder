from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "GW2 WvW Builder API"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "gw2_wvwbuilder"
    DATABASE_URI: Optional[str] = None

    # GW2 API
    GW2_API_BASE_URL: str = "https://api.guildwars2.com/v2"

    class Config:
        case_sensitive = True
        env_file = ".env"

    def get_database_url(self) -> str:
        if self.DATABASE_URI is not None:
            return self.DATABASE_URI
        # Use SQLite for development
        return "sqlite:///./test.db"
        # For PostgreSQL:
        # return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
