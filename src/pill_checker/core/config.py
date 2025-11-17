from functools import lru_cache
from typing import List

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings, validator

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    # Environment - Local Development Only
    APP_ENV: str = "development"  # Fixed to development as per requirements
    DEBUG: bool = True  # Enabled for local development

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "PillChecker"

    # Security
    SECRET_KEY: str = "test-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = []

    # Security
    TRUSTED_HOSTS: List[str] = ["localhost:8080", "127.0.0.1:8080"]
    RATE_LIMIT_PER_SECOND: int = 10
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000

    # DB settings
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = "54322"
    POSTGRES_DB: str = "postgres"

    # Storage Settings
    STORAGE_PATH: str = "./storage"
    STORAGE_BASE_URL: str = "http://localhost:8000"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"

    @validator("ACCESS_TOKEN_EXPIRE_MINUTES", pre=True)
    def validate_token_expire(cls, v):
        """Validate and convert ACCESS_TOKEN_EXPIRE_MINUTES."""
        try:
            return int(str(v).split("#")[0].strip())
        except (ValueError, TypeError):
            return 11520

    @validator("BACKEND_CORS_ORIGINS", "TRUSTED_HOSTS", pre=True)
    def parse_string_list(cls, v):
        """Parse comma-separated string to list."""
        if isinstance(v, str):
            try:
                import json

                return json.loads(v)
            except json.JSONDecodeError:
                return [item.strip() for item in v.split(",") if item.strip()]
        return v

    @validator(
        "RATE_LIMIT_PER_SECOND",
        "RATE_LIMIT_PER_MINUTE",
        "RATE_LIMIT_PER_HOUR",
        pre=True,
    )
    def validate_rate_limits(cls, v):
        """Validate rate limit values."""
        try:
            value = int(str(v))
            if value <= 0:
                raise ValueError("Rate limit must be positive")
            return value
        except (ValueError, TypeError):
            raise ValueError("Rate limit must be a positive integer")

    @validator("SECRET_KEY", pre=True)
    def validate_secret_key(cls, v):
        """Validate that SECRET_KEY is set."""
        if not v:
            raise ValueError("SECRET_KEY environment variable is not set")
        return v

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        database_url = (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
        return database_url

    class Config:
        case_sensitive = True
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
