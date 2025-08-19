"""
Configuration for multilingual worker.
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class MultilingualConfig(BaseSettings):
    """Configuration for multilingual processing."""
    
    # Database settings
    DATABASE_URL: Optional[str] = None
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "postgres")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "comfyrent_production")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "comfyrent_user")
    POSTGRES_PASSWORD: Optional[str] = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_PASSWORD_FILE: str = os.getenv("POSTGRES_PASSWORD_FILE", "/run/secrets/postgres_password")
    
    # API settings
    API_TOKEN: str = "dummy_token_placeholder"
    api_base_url: str = "https://api-statements.tnet.ge/v1/statements"
    request_timeout: int = 30
    delay_between_requests: float = 0.5
    max_retries: int = 3
    
    # Processing settings
    BATCH_SIZE: int = 50
    PROCESS_INTERVAL: int = 300
    MAX_RETRIES: int = 3
    LOG_LEVEL: str = "INFO"
    DEBUG_MODE: bool = False
    
    # Languages to process
    supported_languages: List[str] = ['en', 'ru']
    
    # Processing settings
    max_concurrent_requests: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True
