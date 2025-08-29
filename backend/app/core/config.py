from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GW2 WvW Builder API"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Database
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./gw2_wvwbuilder.db"
    
    # GW2 API Configuration
    GW2_API_BASE_URL: str = "https://api.guildwars2.com/v2"
    GW2_WIKI_API_URL: str = "https://wiki.guildwars2.com/api.php"
    
    # Application Settings
    DEBUG: bool = True
    TESTING: bool = False
    LOG_TO_FILE: bool = False

    # Optional override used by tests
    DATABASE_URL: Optional[str] = None
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        
    def get_database_url(self) -> str:
        """Get the database URL, using test override if provided."""
        return self.DATABASE_URL or self.SQLALCHEMY_DATABASE_URI

# Create settings instance
settings = Settings()
