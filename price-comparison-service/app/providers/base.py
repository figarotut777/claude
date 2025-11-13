"""
Базовый интерфейс для провайдеров маркетплейсов.

Все провайдеры должны наследоваться от BaseProvider и реализовывать
его абстрактные методы.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..models import Product, ProductMeta


class BaseProvider(ABC):
    """
    Абстрактный базовый класс для всех провайдеров маркетплейсов.

    Определяет единый интерфейс для работы с разными маркетплейсами.
    Каждый провайдер должен реализовать три основных метода:
    - search_by_text: поиск товаров по текстовому запросу
    - search_by_product_info: поиск товаров по метаданным
    - parse_product_page: парсинг страницы конкретного товара
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация провайдера.

        :param api_key: API ключ для доступа к официальному API (если есть)
        """
        self.api_key = api_key

    @abstractmethod
    async def search_by_text(
        self, query: str, max_results: int = 10
    ) -> List[Product]:
        """
        Поиск товаров по текстовому запросу.

        :param query: Поисковый запрос (например, "кожаная сумка Feruni")
        :param max_results: Максимальное количество результатов
        :return: Список найденных товаров
        """
        pass

    @abstractmethod
    async def search_by_product_info(
        self, product_meta: ProductMeta, max_results: int = 10
    ) -> List[Product]:
        """
        Поиск товаров по метаданным (бренд, модель, артикул и т.д.).

        Используется для поиска конкретного товара на основе информации,
        извлечённой с другого маркетплейса.

        :param product_meta: Метаданные товара для поиска
        :param max_results: Максимальное количество результатов
        :return: Список найденных товаров
        """
        pass

    @abstractmethod
    async def parse_product_page(self, url: str) -> Optional[ProductMeta]:
        """
        Парсинг страницы товара и извлечение метаданных.

        :param url: URL страницы товара на маркетплейсе
        :return: ProductMeta с извлечёнными данными или None, если парсинг не удался
        """
        pass

    @property
    @abstractmethod
    def marketplace_name(self) -> str:
        """
        Название маркетплейса.

        :return: Строковый идентификатор маркетплейса
        """
        pass

    def is_api_available(self) -> bool:
        """
        Проверяет доступность официального API.

        :return: True, если API ключ настроен и API доступен
        """
        return self.api_key is not None

    async def health_check(self) -> bool:
        """
        Проверка работоспособности провайдера.

        :return: True, если провайдер работает
        """
        # Базовая реализация - можно переопределить в наследниках
        try:
            # Пробуем выполнить простой поиск
            results = await self.search_by_text("test", max_results=1)
            return True
        except Exception:
            return False
