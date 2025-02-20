import os
from functools import lru_cache
from typing import List, Optional

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "PillChecker"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000",  # React default port
        "https://165.232.73.98",
    ]
    
    # Supabase Settings
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")
    
    # Storage
    SUPABASE_STORAGE_BUCKET: str = "pill-images"
    STORAGE_URL: Optional[str] = None

    @property
    def storage_url(self) -> str:
        if not self.STORAGE_URL:
            return f"{self.SUPABASE_URL}/storage/v1/object/public/{self.SUPABASE_STORAGE_BUCKET}"
        return self.STORAGE_URL

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"

    class Config:
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 