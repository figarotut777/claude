"""
Сервис для сравнения цен и создания итогового результата.
"""
import time
from typing import List, Optional, Tuple
from decimal import Decimal

from ..models import (
    Product,
    ProductMatch,
    ComparisonResult,
)
from .search import SearchService
from .matcher import MatcherService


class PriceComparisonService:
    """
    Главный сервис для сравнения цен.

    Объединяет SearchService и MatcherService для создания
    полноценного результата сравнения.
    """

    def __init__(self):
        self.search_service = SearchService()
        self.matcher_service = MatcherService()

    async def compare_by_text(
        self, query: str, max_results_per_marketplace: int = 10
    ) -> ComparisonResult:
        """
        Сравнение цен по текстовому запросу.

        :param query: Поисковый запрос
        :param max_results_per_marketplace: Максимум результатов с каждого маркетплейса
        :return: ComparisonResult с агрегированными данными
        """
        start_time = time.time()

        # 1. Поиск товаров на всех маркетплейсах
        products = await self.search_service.search_by_text(
            query, max_results_per_marketplace
        )

        # 2. Сопоставление одинаковых товаров
        matches = self.matcher_service.match_products(products)

        # 3. Аналитика
        cheapest = self._find_cheapest_overall(products)
        price_range = self._calculate_price_range(products)

        # 4. Формирование результата
        search_time_ms = (time.time() - start_time) * 1000

        return ComparisonResult(
            query=query,
            matches=matches,
            total_products=len(products),
            total_unique_products=len(matches),
            cheapest_overall=cheapest,
            price_range=price_range,
            marketplaces_searched=self.search_service.get_active_marketplaces(),
            search_time_ms=search_time_ms,
        )

    async def compare_by_url(
        self, url: str, max_results_per_marketplace: int = 10
    ) -> ComparisonResult:
        """
        Сравнение цен по URL товара.

        Алгоритм:
        1. Парсим URL и извлекаем метаданные товара
        2. Ищем этот же товар на других маркетплейсах
        3. Сопоставляем и сравниваем цены

        :param url: URL товара на одном из маркетплейсов
        :param max_results_per_marketplace: Максимум результатов с каждого маркетплейса
        :return: ComparisonResult
        """
        start_time = time.time()

        # 1. Парсинг URL
        product_meta = await self.search_service.parse_product_from_url(url)

        if not product_meta:
            # Не удалось распарсить URL
            return ComparisonResult(
                query=url,
                matches=[],
                total_products=0,
                total_unique_products=0,
                cheapest_overall=None,
                price_range=None,
                marketplaces_searched=self.search_service.get_active_marketplaces(),
                search_time_ms=(time.time() - start_time) * 1000,
            )

        # 2. Поиск на других площадках
        products = await self.search_service.search_by_product_info(
            product_meta, max_results_per_marketplace
        )

        # 3. Сопоставление
        matches = self.matcher_service.match_products(products)

        # 4. Аналитика
        cheapest = self._find_cheapest_overall(products)
        price_range = self._calculate_price_range(products)

        search_time_ms = (time.time() - start_time) * 1000

        # Используем название товара как query, если есть
        query_display = product_meta.name or url

        return ComparisonResult(
            query=query_display,
            matches=matches,
            total_products=len(products),
            total_unique_products=len(matches),
            cheapest_overall=cheapest,
            price_range=price_range,
            marketplaces_searched=self.search_service.get_active_marketplaces(),
            search_time_ms=search_time_ms,
        )

    def _find_cheapest_overall(self, products: List[Product]) -> Optional[Product]:
        """
        Находит самый дешёвый товар среди всех.
        """
        if not products:
            return None

        return min(products, key=lambda p: p.price)

    def _calculate_price_range(
        self, products: List[Product]
    ) -> Optional[Tuple[Decimal, Decimal]]:
        """
        Вычисляет диапазон цен (min, max).
        """
        if not products:
            return None

        prices = [p.price for p in products]
        return (min(prices), max(prices))
