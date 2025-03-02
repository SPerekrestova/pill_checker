import os
from functools import lru_cache
from typing import List, Optional

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings, validator

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    # Environment
    APP_ENV: str = "development"
    DEBUG: bool = True

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "PillChecker"

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = []

    # Security
    TRUSTED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    RATE_LIMIT_PER_SECOND: int = 10
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000

    # Supabase Settings
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_JWT_SECRET: str = None
    SUPABASE_STORAGE_BUCKET: str = "pill-images"
    SUPABASE_ANON_KEY: str = None
    SUPABASE_SERVICE_ROLE_KEY: str = None

    # Database - The actual values will be set based on APP_ENV
    DATABASE_USER: str = None
    DATABASE_PASSWORD: str = None
    DATABASE_HOST: str = None
    DATABASE_PORT: str = None
    DATABASE_NAME: str = None

    # Storage
    STORAGE_URL: Optional[str] = None

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

    @validator("RATE_LIMIT_PER_SECOND", "RATE_LIMIT_PER_MINUTE", "RATE_LIMIT_PER_HOUR", pre=True)
    def validate_rate_limits(cls, v):
        """Validate rate limit values."""
        try:
            value = int(str(v))
            if value <= 0:
                raise ValueError("Rate limit must be positive")
            return value
        except (ValueError, TypeError):
            raise ValueError("Rate limit must be a positive integer")

    @validator(
        "DATABASE_USER",
        "DATABASE_PASSWORD",
        "DATABASE_HOST",
        "DATABASE_PORT",
        "DATABASE_NAME",
        pre=True,
    )
    def set_db_credentials(cls, v, values, field):
        """Set database credentials based on environment."""
        env_prefix = {"development": "DEV_", "testing": "TEST_", "production": "PROD_"}.get(
            values.get("APP_ENV", "development"), "DEV_"
        )

        env_var = f"{env_prefix}{field.name}"
        value = os.getenv(env_var)
        if not value and field.name != "DATABASE_PASSWORD":  # Allow empty password
            raise ValueError(f"Database environment variable {env_var} is not set")
        return value or ""  # Return empty string for empty password

    @validator("SECRET_KEY", pre=True)
    def validate_secret_key(cls, v):
        """Validate that SECRET_KEY is set."""
        if not v:
            raise ValueError("SECRET_KEY environment variable is not set")
        return v

    @validator("SUPABASE_URL", "SUPABASE_KEY", pre=True)
    def validate_supabase_settings(cls, v, field):
        """Validate that required Supabase settings are set."""
        if not v:
            raise ValueError(f"{field.name} environment variable is not set")
        return v

    @validator("SUPABASE_JWT_SECRET", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY", pre=True)
    def validate_optional_supabase_settings(cls, v, field):
        """Validate optional Supabase settings."""
        # These are not strictly required for all functionalities
        if not v:
            return os.getenv(field.name, None)
        return v

    @property
    def storage_url(self) -> str:
        """Get storage URL."""
        if not self.STORAGE_URL:
            return f"{self.SUPABASE_URL}/storage/v1/object/public/{self.SUPABASE_STORAGE_BUCKET}"
        return self.STORAGE_URL

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Construct database URI."""
        sslmode = "require" if self.APP_ENV == "production" else "disable"
        return f"postgresql+psycopg2://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}?sslmode={sslmode}"

    class Config:
        case_sensitive = True
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
