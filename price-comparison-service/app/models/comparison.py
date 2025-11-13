"""
Модели для результатов сравнения цен.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Tuple
from decimal import Decimal
from .product import Product
from .enums import MatchingMethod


class ProductMatch(BaseModel):
    """
    Группа одинаковых товаров с разных площадок.

    Представляет один и тот же товар, найденный на разных маркетплейсах
    и/или у разных продавцов.
    """

    match_id: str = Field(..., description="ID группы совпадений")

    products: List[Product] = Field(
        ...,
        description="Список товаров (один и тот же товар с разных площадок)"
    )

    # Метаданные сопоставления
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Уверенность в совпадении (0.0-1.0)"
    )

    matching_method: MatchingMethod = Field(
        ...,
        description="Метод, которым товары были сопоставлены"
    )

    # Аналитика по ценам
    cheapest_offer: Product = Field(
        ...,
        description="Самое дешёвое предложение в группе"
    )

    most_expensive_offer: Product = Field(
        ...,
        description="Самое дорогое предложение в группе"
    )

    price_difference: Decimal = Field(
        ...,
        description="Разница между самой дорогой и дешёвой ценой"
    )

    price_difference_percent: float = Field(
        ...,
        description="Разница в процентах"
    )

    avg_price: Decimal = Field(
        ...,
        description="Средняя цена среди всех предложений"
    )

    # Представительное название для группы
    representative_name: str = Field(
        ...,
        description="Наиболее полное название товара из группы"
    )

    representative_brand: Optional[str] = Field(
        None,
        description="Бренд товара"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "match_id": "match_abc123",
                "products": [],  # массив Product
                "confidence": 0.95,
                "matching_method": "brand_model",
                "cheapest_offer": {},
                "most_expensive_offer": {},
                "price_difference": "2000.00",
                "price_difference_percent": 28.57,
                "avg_price": "5499.00",
                "representative_name": "Сумка кожаная женская Feruni FRN-2024-BLK",
                "representative_brand": "Feruni"
            }
        }


class ComparisonResult(BaseModel):
    """
    Общий результат сравнения цен.

    Возвращается API и содержит все найденные совпадения с аналитикой.
    """

    query: str = Field(..., description="Исходный запрос пользователя")

    matches: List[ProductMatch] = Field(
        default_factory=list,
        description="Список групп совпадающих товаров"
    )

    total_products: int = Field(
        ...,
        description="Общее количество найденных товаров (офферов)"
    )

    total_unique_products: int = Field(
        ...,
        description="Количество уникальных товаров (групп)"
    )

    # Глобальная аналитика
    cheapest_overall: Optional[Product] = Field(
        None,
        description="Самое дешёвое предложение среди всех найденных"
    )

    price_range: Optional[Tuple[Decimal, Decimal]] = Field(
        None,
        description="Диапазон цен (min, max)"
    )

    # Статистика по маркетплейсам
    marketplaces_searched: List[str] = Field(
        default_factory=list,
        description="Список маркетплейсов, где производился поиск"
    )

    search_time_ms: Optional[float] = Field(
        None,
        description="Время выполнения поиска в миллисекундах"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "кожаная сумка Feruni",
                "matches": [],
                "total_products": 15,
                "total_unique_products": 3,
                "cheapest_overall": {},
                "price_range": ["3999.00", "7999.00"],
                "marketplaces_searched": ["wildberries", "ozon", "yandex_market"],
                "search_time_ms": 1250.5
            }
        }


class SearchByTextRequest(BaseModel):
    """Запрос на поиск по тексту"""
    query: str = Field(..., min_length=1, description="Поисковый запрос")
    max_results_per_marketplace: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Максимум результатов с каждого маркетплейса"
    )


class SearchByUrlRequest(BaseModel):
    """Запрос на поиск по URL"""
    url: str = Field(..., description="URL товара на маркетплейсе")
    max_results_per_marketplace: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Максимум результатов с каждого маркетплейса"
    )
