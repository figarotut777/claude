"""
Модели товаров и предложений.
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any, List
from decimal import Decimal
from datetime import datetime
from .enums import Marketplace, Currency


class Product(BaseModel):
    """
    Товар с конкретного маркетплейса.

    Представляет одно предложение (offer) от одного продавца на одной площадке.
    """

    # Идентификация
    id: str = Field(..., description="Внутренний ID для нашей системы")
    marketplace: Marketplace = Field(..., description="Маркетплейс")
    external_id: str = Field(..., description="ID товара на маркетплейсе")

    # Основная информация
    name: str = Field(..., description="Название товара")
    brand: Optional[str] = Field(None, description="Бренд/производитель")
    model: Optional[str] = Field(None, description="Модель товара")

    # Идентификаторы для сопоставления
    gtin: Optional[str] = Field(
        None,
        description="Global Trade Item Number (EAN/UPC/штрих-код)"
    )
    article: Optional[str] = Field(
        None,
        description="Артикул производителя"
    )
    sku: Optional[str] = Field(
        None,
        description="SKU продавца"
    )

    # Цена
    price: Decimal = Field(..., description="Цена в указанной валюте")
    original_price: Optional[Decimal] = Field(
        None,
        description="Оригинальная цена (до скидки)"
    )
    currency: Currency = Field(default=Currency.RUB, description="Валюта цены")

    # Продавец
    seller_name: Optional[str] = Field(None, description="Название продавца")
    seller_rating: Optional[float] = Field(
        None,
        ge=0.0,
        le=5.0,
        description="Рейтинг продавца (0-5)"
    )

    # Ссылки
    url: str = Field(..., description="URL карточки товара")
    image_urls: List[str] = Field(
        default_factory=list,
        description="Список URL изображений"
    )

    # Характеристики для сопоставления
    attributes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Характеристики товара (цвет, размер, материал и т.д.)"
    )

    # Дополнительно
    description: Optional[str] = Field(None, description="Описание товара")
    in_stock: bool = Field(default=True, description="Доступность товара")

    # Метаданные
    fetched_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Когда данные были получены"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "wbr_12345678",
                "marketplace": "wildberries",
                "external_id": "12345678",
                "name": "Сумка кожаная женская Feruni",
                "brand": "Feruni",
                "model": "FRN-2024-BLK",
                "gtin": "4627090123456",
                "article": "FRN2024",
                "price": "4999.00",
                "original_price": "7999.00",
                "currency": "RUB",
                "seller_name": "Feruni Official",
                "seller_rating": 4.8,
                "url": "https://www.wildberries.ru/catalog/12345678/detail.aspx",
                "image_urls": [
                    "https://basket-01.wb.ru/vol123/part12345/12345678/images/big/1.jpg"
                ],
                "attributes": {
                    "Цвет": "Черный",
                    "Материал": "Натуральная кожа",
                    "Размер": "30x25x10 см"
                },
                "in_stock": True
            }
        }


class ProductMeta(BaseModel):
    """
    Метаданные товара для поиска.

    Используется при поиске по URL - извлечённая информация о товаре,
    которую нужно найти на других площадках.
    """

    name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    gtin: Optional[str] = None
    article: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)
    image_urls: List[str] = Field(default_factory=list)

    def has_strong_identifiers(self) -> bool:
        """Проверяет наличие сильных идентификаторов для поиска"""
        return bool(self.gtin or (self.brand and self.model) or self.article)
