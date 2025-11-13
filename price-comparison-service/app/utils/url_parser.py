"""
Утилиты для парсинга URL маркетплейсов.
"""
import re
from urllib.parse import urlparse, parse_qs
from typing import Optional, Tuple
from ..models.enums import Marketplace


def detect_marketplace(url: str) -> Optional[Marketplace]:
    """
    Определяет маркетплейс по URL.

    :param url: URL товара
    :return: Marketplace enum или None, если не определён
    """
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    if "wildberries.ru" in domain or "wb.ru" in domain:
        return Marketplace.WILDBERRIES

    if "ozon.ru" in domain:
        return Marketplace.OZON

    if "market.yandex.ru" in domain or "pokupki.market.yandex.ru" in domain:
        return Marketplace.YANDEX_MARKET

    return None


def extract_wildberries_id(url: str) -> Optional[str]:
    """
    Извлекает ID товара из URL Wildberries.

    Примеры URL:
    - https://www.wildberries.ru/catalog/12345678/detail.aspx
    - https://www.wb.ru/catalog/12345678/detail.aspx?targetUrl=SP
    """
    # Паттерн: /catalog/{ID}/detail
    match = re.search(r"/catalog/(\d+)/detail", url)
    if match:
        return match.group(1)
    return None


def extract_ozon_id(url: str) -> Optional[str]:
    """
    Извлекает ID товара из URL Ozon.

    Примеры URL:
    - https://www.ozon.ru/product/sumka-feruni-123456789/
    - https://www.ozon.ru/product/123456789/
    """
    # Паттерн 1: /product/{slug}-{ID}/
    match = re.search(r"/product/[a-z0-9-]+-(\d+)/?", url)
    if match:
        return match.group(1)

    # Паттерн 2: /product/{ID}/
    match = re.search(r"/product/(\d+)/?", url)
    if match:
        return match.group(1)

    return None


def extract_yandex_market_id(url: str) -> Optional[str]:
    """
    Извлекает ID товара из URL Yandex Market.

    Примеры URL:
    - https://market.yandex.ru/product--sumka/123456789
    - https://market.yandex.ru/product/123456789
    """
    # Паттерн 1: /product--{slug}/{ID}
    match = re.search(r"/product--[^/]+/(\d+)", url)
    if match:
        return match.group(1)

    # Паттерн 2: /product/{ID}
    match = re.search(r"/product/(\d+)", url)
    if match:
        return match.group(1)

    # Паттерн 3: из query параметров
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    if "productId" in query_params:
        return query_params["productId"][0]

    return None


def parse_marketplace_url(url: str) -> Tuple[Optional[Marketplace], Optional[str]]:
    """
    Универсальный парсер URL маркетплейсов.

    :param url: URL товара
    :return: Tuple (Marketplace, external_id) или (None, None)
    """
    marketplace = detect_marketplace(url)

    if marketplace is None:
        return None, None

    external_id = None

    if marketplace == Marketplace.WILDBERRIES:
        external_id = extract_wildberries_id(url)
    elif marketplace == Marketplace.OZON:
        external_id = extract_ozon_id(url)
    elif marketplace == Marketplace.YANDEX_MARKET:
        external_id = extract_yandex_market_id(url)

    return marketplace, external_id


def is_valid_marketplace_url(url: str) -> bool:
    """
    Проверяет, является ли URL валидным URL маркетплейса.

    :param url: URL для проверки
    :return: True если URL валиден
    """
    marketplace, external_id = parse_marketplace_url(url)
    return marketplace is not None and external_id is not None
