"""
Конфигурация приложения.
Загружает настройки из переменных окружения с использованием pydantic-settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Настройки приложения"""

    # Application
    app_name: str = "Price Comparison Service"
    app_version: str = "0.1.0"
    debug: bool = True

    # API Keys для маркетплейсов (когда появятся)
    yandex_market_api_key: Optional[str] = None
    wildberries_api_key: Optional[str] = None
    ozon_api_key: Optional[str] = None

    # Provider toggles
    enable_yandex_market: bool = True
    enable_wildberries: bool = True
    enable_ozon: bool = True

    # HTTP настройки для парсинга
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    request_timeout: int = 10

    # Matcher настройки
    min_similarity_threshold: float = 0.85
    use_image_comparison: bool = False

    # Cache (для будущей реализации)
    cache_enabled: bool = False
    cache_ttl: int = 3600

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Глобальный экземпляр настроек
settings = Settings()
