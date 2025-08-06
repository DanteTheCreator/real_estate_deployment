"""
Configuration for multilingual worker.
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class MultilingualConfig(BaseSettings):
    """Configuration for multilingual processing."""
    
    # Database settings
    DATABASE_URL: str
    
    # API settings
    API_TOKEN: str
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
