"""
Сервис для координации поиска по всем маркетплейсам.
"""
import asyncio
from typing import List, Optional
from ..models import Product, ProductMeta
from ..providers import (
    BaseProvider,
    WildberriesProvider,
    OzonProvider,
    YandexMarketProvider,
)
from ..config import settings


class SearchService:
    """
    Координирует поиск по нескольким маркетплейсам параллельно.
    """

    def __init__(self):
        """
        Инициализация провайдеров на основе настроек.
        """
        self.providers: List[BaseProvider] = []

        # Инициализируем провайдеры в зависимости от настроек
        if settings.enable_wildberries:
            self.providers.append(
                WildberriesProvider(api_key=settings.wildberries_api_key)
            )

        if settings.enable_ozon:
            self.providers.append(OzonProvider(api_key=settings.ozon_api_key))

        if settings.enable_yandex_market:
            self.providers.append(
                YandexMarketProvider(api_key=settings.yandex_market_api_key)
            )

    async def search_by_text(
        self, query: str, max_results_per_marketplace: int = 10
    ) -> List[Product]:
        """
        Поиск товаров по текстовому запросу на всех доступных маркетплейсах.

        Выполняет поиск параллельно для ускорения.

        :param query: Поисковый запрос
        :param max_results_per_marketplace: Максимум результатов с каждого маркетплейса
        :return: Агрегированный список товаров со всех площадок
        """
        if not self.providers:
            return []

        # Запускаем поиск параллельно на всех провайдерах
        tasks = [
            provider.search_by_text(query, max_results_per_marketplace)
            for provider in self.providers
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Собираем все товары, игнорируя ошибки
        all_products: List[Product] = []
        for result in results:
            if isinstance(result, list):
                all_products.extend(result)
            # Если был exception, просто пропускаем этот результат
            # В production здесь нужно логирование

        return all_products

    async def search_by_product_info(
        self, product_meta: ProductMeta, max_results_per_marketplace: int = 10
    ) -> List[Product]:
        """
        Поиск товаров по метаданным на всех доступных маркетплейсах.

        Используется для поиска конкретного товара после парсинга URL.

        :param product_meta: Метаданные товара
        :param max_results_per_marketplace: Максимум результатов с каждого маркетплейса
        :return: Список найденных товаров
        """
        if not self.providers:
            return []

        tasks = [
            provider.search_by_product_info(product_meta, max_results_per_marketplace)
            for provider in self.providers
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_products: List[Product] = []
        for result in results:
            if isinstance(result, list):
                all_products.extend(result)

        return all_products

    async def parse_product_from_url(self, url: str) -> Optional[ProductMeta]:
        """
        Парсит URL товара и извлекает метаданные.

        Автоматически определяет нужный провайдер по URL.

        :param url: URL товара на маркетплейсе
        :return: ProductMeta или None
        """
        # Пробуем каждый провайдер, пока не найдём подходящий
        for provider in self.providers:
            try:
                product_meta = await provider.parse_product_page(url)
                if product_meta:
                    return product_meta
            except Exception:
                # В production - логирование
                continue

        return None

    def get_active_marketplaces(self) -> List[str]:
        """
        Возвращает список активных маркетплейсов.

        :return: Список названий маркетплейсов
        """
        return [provider.marketplace_name for provider in self.providers]
