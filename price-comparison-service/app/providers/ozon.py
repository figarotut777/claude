"""
Провайдер для Ozon.

ТЕКУЩАЯ РЕАЛИЗАЦИЯ: Заглушка с фейковыми данными.

TODO для production:
1. Проверить наличие официального Ozon API для партнёров
2. Реализовать парсинг через API или HTML/JSON endpoints
3. Учесть особенности работы с Ozon (авторизация, cookies, anti-bot)
4. Добавить кеширование результатов
"""
from typing import List, Optional
import uuid
from decimal import Decimal
from .base import BaseProvider
from ..models import Product, ProductMeta, Marketplace, Currency
from ..utils import parse_marketplace_url


class OzonProvider(BaseProvider):
    """
    Провайдер для Ozon маркетплейса.
    """

    @property
    def marketplace_name(self) -> str:
        return "ozon"

    async def search_by_text(
        self, query: str, max_results: int = 10
    ) -> List[Product]:
        """
        Поиск товаров по текстовому запросу на Ozon.

        ЗАГЛУШКА: Возвращает фейковые данные.

        В production:
        - URL поиска: https://www.ozon.ru/search/?text={query}
        - Может использоваться API endpoint: /api/composer-api.bx/page/json/v2
        - Требуется анализ network requests в браузере
        """
        fake_products = []

        if "feruni" in query.lower() or "сумка" in query.lower():
            fake_products.extend([
                Product(
                    id=f"ozon_{uuid.uuid4().hex[:8]}",
                    marketplace=Marketplace.OZON,
                    external_id="234567890",
                    name="Сумка женская Feruni из натуральной кожи FRN-2024-BLK",
                    brand="Feruni",
                    model="FRN-2024-BLK",
                    gtin="4627090123456",
                    article="FRN2024",
                    price=Decimal("5299.00"),
                    original_price=Decimal("8999.00"),
                    currency=Currency.RUB,
                    seller_name="OZON",
                    seller_rating=4.9,
                    url="https://www.ozon.ru/product/sumka-feruni-234567890/",
                    image_urls=[
                        "https://cdn1.ozone.ru/s3/multimedia-1/c1000/234567890.jpg"
                    ],
                    attributes={
                        "Цвет": "Черный",
                        "Материал": "Натуральная кожа",
                        "Размер": "30x25x10 см",
                        "Вес": "0.8 кг"
                    },
                    description="Стильная кожаная сумка от Feruni",
                    in_stock=True,
                ),
                Product(
                    id=f"ozon_{uuid.uuid4().hex[:8]}",
                    marketplace=Marketplace.OZON,
                    external_id="345678901",
                    name="Feruni FRN-2024-BLK сумка кожаная женская черная",
                    brand="Feruni",
                    model="FRN-2024-BLK",
                    gtin="4627090123456",
                    article="FRN2024",
                    price=Decimal("4799.00"),
                    currency=Currency.RUB,
                    seller_name="Bags & Style",
                    seller_rating=4.6,
                    url="https://www.ozon.ru/product/345678901/",
                    image_urls=[
                        "https://cdn1.ozone.ru/s3/multimedia-2/c1000/345678901.jpg"
                    ],
                    attributes={
                        "Цвет": "Черный",
                        "Материал": "Натуральная кожа",
                        "Размер": "30x25x10 см"
                    },
                    in_stock=True,
                ),
            ])

        return fake_products[:max_results]

    async def search_by_product_info(
        self, product_meta: ProductMeta, max_results: int = 10
    ) -> List[Product]:
        """
        Поиск товаров по метаданным.

        В production:
        - Приоритет: GTIN > артикул > бренд+модель > название
        - Использовать фильтры API для точности
        """
        search_query = ""

        if product_meta.gtin:
            # GTIN - самый точный идентификатор
            search_query = product_meta.gtin
        elif product_meta.brand and product_meta.model:
            search_query = f"{product_meta.brand} {product_meta.model}"
        elif product_meta.brand and product_meta.name:
            search_query = f"{product_meta.brand} {product_meta.name}"
        elif product_meta.name:
            search_query = product_meta.name

        if not search_query.strip():
            return []

        return await self.search_by_text(search_query.strip(), max_results)

    async def parse_product_page(self, url: str) -> Optional[ProductMeta]:
        """
        Парсинг страницы товара на Ozon.

        В production:
        - Ozon часто использует API endpoints для загрузки данных
        - Нужно проанализировать network requests
        - Может потребоваться Playwright для динамического контента
        """
        marketplace, external_id = parse_marketplace_url(url)

        if marketplace != Marketplace.OZON or not external_id:
            return None

        # Фейковые данные
        return ProductMeta(
            name="Сумка женская Feruni из натуральной кожи FRN-2024-BLK",
            brand="Feruni",
            model="FRN-2024-BLK",
            gtin="4627090123456",
            article="FRN2024",
            attributes={
                "Цвет": "Черный",
                "Материал": "Натуральная кожа",
                "Размер": "30x25x10 см",
                "Вес": "0.8 кг"
            },
            image_urls=[
                "https://cdn1.ozone.ru/s3/multimedia-1/c1000/234567890.jpg"
            ],
        )
