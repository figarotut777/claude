"""
Перечисления для различных типов и статусов.
"""
from enum import Enum


class Marketplace(str, Enum):
    """Маркетплейсы"""
    YANDEX_MARKET = "yandex_market"
    WILDBERRIES = "wildberries"
    OZON = "ozon"
    # Легко добавить новые:
    # ALIEXPRESS = "aliexpress"
    # SBER_MEGAMARKET = "sber_megamarket"


class MatchingMethod(str, Enum):
    """Методы сопоставления товаров"""
    GTIN = "gtin"  # По штрих-коду/EAN
    BRAND_MODEL = "brand_model"  # По бренду + модели
    FUZZY_NAME = "fuzzy_name"  # По похожему названию
    ATTRIBUTES = "attributes"  # По характеристикам
    IMAGE_HASH = "image_hash"  # По изображению (будущая фича)
    MANUAL = "manual"  # Ручное сопоставление


class Currency(str, Enum):
    """Валюты"""
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"
