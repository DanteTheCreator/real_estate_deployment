from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv
import secrets

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "postgresql://comfyrent_user:password@postgres:5432/comfyrent_production")
    
    # Security settings
    secret_key: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(64))
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(64))
    algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Environment settings
    environment: str = os.getenv("ENVIRONMENT", "production")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # CORS settings - more restrictive for production
    cors_origins: str = os.getenv("CORS_ORIGINS", "https://comfyrent.homes,https://www.comfyrent.homes")
    
    # App settings
    app_name: str = os.getenv("APP_NAME", "ComfyRent API")
    version: str = "1.0.0"
    
    # MinIO settings
    minio_endpoint: str = os.getenv("MINIO_ENDPOINT", "minio:9000")
    minio_access_key: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    minio_secret_key: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    minio_bucket_name: str = os.getenv("MINIO_BUCKET_NAME", "comfyrent-assets")
    minio_secure: bool = os.getenv("MINIO_SECURE", "false").lower() == "true"
    
    # Redis settings
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    @property
    def redis_url_with_auth(self) -> str:
        """Get Redis URL with authentication from secret file"""
        redis_password_file = os.getenv("REDIS_PASSWORD_FILE", "/run/secrets/redis_password")
        if os.path.exists(redis_password_file):
            try:
                with open(redis_password_file, 'r') as f:
                    password = f.read().strip()
                # Parse the base URL and add authentication
                if self.redis_url.startswith("redis://"):
                    return f"redis://:{password}@{self.redis_url[8:]}"
                return self.redis_url
            except Exception as e:
                print(f"Warning: Could not read Redis password from {redis_password_file}: {e}")
                return self.redis_url
        return self.redis_url
    
    # Rate limiting
    rate_limit_enabled: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    rate_limit_requests_per_minute: int = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "100"))
    
    # Security headers
    security_headers_enabled: bool = os.getenv("SECURITY_HEADERS_ENABLED", "true").lower() == "true"
    
    # Email settings
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from_email: str = os.getenv("SMTP_FROM_EMAIL", "noreply@comfyrent.homes")
    smtp_from_name: str = os.getenv("SMTP_FROM_NAME", "ComfyRent")
    
    # Monitoring
    sentry_dsn: str = os.getenv("SENTRY_DSN", "")
    monitoring_enabled: bool = os.getenv("MONITORING_ENABLED", "false").lower() == "true"
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(',') if origin.strip()]
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }

settings = Settings()
