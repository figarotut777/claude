from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Price-Scanner"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/price_scanner"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL_IMAGE_SEARCH: int = 3600
    CACHE_TTL_TEXT_SEARCH: int = 1800
    CACHE_TTL_URL_PARSE: int = 7200
    CACHE_TTL_PRODUCT: int = 86400

    # API Keys
    GOOGLE_VISION_API_KEY: str = ""
    AMAZON_API_KEY: str = ""
    EBAY_API_KEY: str = ""
    ALIEXPRESS_API_KEY: str = ""

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # Rate Limiting
    RATE_LIMIT_FREE: int = 10
    RATE_LIMIT_PRO: int = 1000
    RATE_LIMIT_ENTERPRISE: int = 10000

    # Services URLs
    IMAGE_SEARCH_SERVICE_URL: str = "http://localhost:8001"
    TEXT_SEARCH_SERVICE_URL: str = "http://localhost:8002"
    URL_PARSER_SERVICE_URL: str = "http://localhost:8003"
    MARKETPLACE_SERVICE_URL: str = "http://localhost:8004"
    NORMALIZER_SERVICE_URL: str = "http://localhost:8005"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
