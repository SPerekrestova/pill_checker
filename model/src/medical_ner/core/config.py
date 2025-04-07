from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    # Model settings
    SPACY_MODEL: str = Field(default="en_ner_bc5cdr_md", env="SPACY_MODEL")
    LINKER_NAME: str = Field(default="rxnorm", env="LINKER_NAME")

    # API settings
    API_PREFIX: str = Field(default="/api", env="API_PREFIX")
    DEBUG: bool = Field(default=False, env="DEBUG")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # Entity linking
    ENTITY_SCORE_THRESHOLD: float = Field(default=0.7, env="ENTITY_SCORE_THRESHOLD")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()