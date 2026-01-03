"""
Клиент для работы с Wildberries API
Поддерживает получение данных о продажах, заказах и остатках
"""

import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class WildberriesAPIClient:
    """Клиент для работы с API Wildberries Supplier Stats"""

    # Базовые URL для API
    BASE_URL = "https://statistics-api.wildberries.ru"
    CONTENT_URL = "https://suppliers-api.wildberries.ru"

    def __init__(self, api_key: str, timeout: int = 30, max_retries: int = 3):
        """
        Инициализация клиента WB API

        Args:
            api_key: API ключ для доступа к WB API
            timeout: Таймаут запросов в секундах
            max_retries: Максимальное количество повторных попыток
        """
        self.api_key = api_key
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)

        # Настройка сессии с retry логикой
        self.session = requests.Session()

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,  # Экспоненциальная задержка: 1s, 2s, 4s
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Установка заголовков
        self.session.headers.update({
            'Authorization': api_key,
            'Content-Type': 'application/json'
        })

    def _make_request(self, method: str, url: str, **kwargs) -> Optional[Dict]:
        """
        Выполнение HTTP запроса с обработкой ошибок

        Args:
            method: HTTP метод (GET, POST и т.д.)
            url: URL для запроса
            **kwargs: Дополнительные параметры для requests

        Returns:
            JSON ответ или None в случае ошибки
        """
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )

            # Логирование запроса
            self.logger.debug(f"{method} {url} -> {response.status_code}")

            # Проверка статуса ответа
            response.raise_for_status()

            # Парсинг JSON
            return response.json()

        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP ошибка при запросе {url}: {e}")
            if e.response.status_code == 401:
                self.logger.error("Ошибка авторизации! Проверьте API ключ")
            elif e.response.status_code == 429:
                self.logger.error("Превышен лимит запросов! Подождите и попробуйте снова")
            return None

        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Ошибка подключения к {url}: {e}")
            return None

        except requests.exceptions.Timeout as e:
            self.logger.error(f"Таймаут запроса к {url}: {e}")
            return None

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при запросе к {url}: {e}")
            return None

        except ValueError as e:
            self.logger.error(f"Ошибка парсинга JSON ответа от {url}: {e}")
            return None

    def get_sales(self, date_from: str, flag: int = 0) -> List[Dict]:
        """
        Получение данных о продажах

        Args:
            date_from: Дата начала в формате RFC3339 (например: 2024-01-01T00:00:00Z)
            flag: Если 0 - возвращает данные с date_from, если 1 - данные >= date_from

        Returns:
            Список продаж
        """
        url = f"{self.BASE_URL}/api/v1/supplier/sales"
        params = {
            'dateFrom': date_from,
            'flag': flag
        }

        self.logger.info(f"Запрос продаж с {date_from}")

        response = self._make_request('GET', url, params=params)

        if response is not None:
            sales_count = len(response) if isinstance(response, list) else 0
            self.logger.info(f"Получено {sales_count} записей о продажах")
            return response if isinstance(response, list) else []

        return []

    def get_orders(self, date_from: str, flag: int = 0) -> List[Dict]:
        """
        Получение данных о заказах

        Args:
            date_from: Дата начала в формате RFC3339
            flag: Если 0 - возвращает данные с date_from, если 1 - данные >= date_from

        Returns:
            Список заказов
        """
        url = f"{self.BASE_URL}/api/v1/supplier/orders"
        params = {
            'dateFrom': date_from,
            'flag': flag
        }

        self.logger.info(f"Запрос заказов с {date_from}")

        response = self._make_request('GET', url, params=params)

        if response is not None:
            orders_count = len(response) if isinstance(response, list) else 0
            self.logger.info(f"Получено {orders_count} записей о заказах")
            return response if isinstance(response, list) else []

        return []

    def get_stocks(self, date_from: str = None) -> List[Dict]:
        """
        Получение данных об остатках товаров на складах WB
        ВАЖНО: API stocks не поддерживает параметр dateFrom!
        Возвращает текущие остатки (обновляется каждые 30 минут)

        Args:
            date_from: УСТАРЕЛ - игнорируется (оставлен для совместимости)

        Returns:
            Список остатков
        """
        url = f"{self.BASE_URL}/api/v1/supplier/stocks"

        # ИСПРАВЛЕНО: убрали параметры - API stocks не принимает dateFrom
        # Передача dateFrom вызывает 400 Bad Request
        params = {}

        self.logger.info("Запрос данных об остатках (текущее состояние)")

        response = self._make_request('GET', url, params=params)

        if response is not None:
            stocks_count = len(response) if isinstance(response, list) else 0
            self.logger.info(f"Получено {stocks_count} записей об остатках")
            return response if isinstance(response, list) else []

        return []

    def get_incomes(self, date_from: str) -> List[Dict]:
        """
        Получение данных о поставках

        Args:
            date_from: Дата начала в формате RFC3339

        Returns:
            Список поставок
        """
        url = f"{self.BASE_URL}/api/v1/supplier/incomes"
        params = {'dateFrom': date_from}

        self.logger.info(f"Запрос поставок с {date_from}")

        response = self._make_request('GET', url, params=params)

        if response is not None:
            incomes_count = len(response) if isinstance(response, list) else 0
            self.logger.info(f"Получено {incomes_count} записей о поставках")
            return response if isinstance(response, list) else []

        return []

    def get_report_detail_by_period(self, date_from: str, date_to: str,
                                    limit: int = 100000, rrdid: int = 0) -> List[Dict]:
        """
        Получение детализированного отчета о продажах за период
        ВАЖНО: С января 2025 используется API v5 (было v1)

        Args:
            date_from: Дата начала (RFC3339, datetime разрешен)
            date_to: Дата окончания (только дата, без времени!)
            limit: Максимальное количество записей
            rrdid: Уникальный идентификатор строки отчета (для пагинации)

        Returns:
            Список детальных данных
        """
        # ИСПРАВЛЕНО: обновлен эндпоинт с v1 на v5 (актуально для 2025)
        url = f"{self.BASE_URL}/api/v5/supplier/reportDetailByPeriod"

        # Форматирование дат согласно требованиям WB API v5:
        # dateFrom - может быть datetime, dateTo - только дата
        try:
            # Убираем время из dateTo, оставляем только дату
            if 'T' in date_to:
                date_to = date_to.split('T')[0]
        except Exception as e:
            self.logger.warning(f"Ошибка форматирования dateTo: {e}")

        params = {
            'dateFrom': date_from,
            'dateTo': date_to,
            'limit': limit,
            'rrdid': rrdid
        }

        self.logger.info(f"Запрос детального отчета v5 с {date_from} по {date_to}")

        response = self._make_request('GET', url, params=params)

        if response is not None:
            report_count = len(response) if isinstance(response, list) else 0
            self.logger.info(f"Получено {report_count} записей детального отчета")
            return response if isinstance(response, list) else []

        return []

    def get_all_data_for_period(self, days_back: int = 7) -> Dict[str, List[Dict]]:
        """
        Получение всех данных (продажи, заказы, остатки, финансовый отчёт) за указанный период

        Args:
            days_back: Количество дней назад от текущей даты

        Returns:
            Словарь с ключами 'sales', 'orders', 'stocks', 'financial_report'
        """
        # Вычисление даты начала и конца
        date_to = datetime.utcnow().isoformat() + 'Z'
        date_from = (datetime.utcnow() - timedelta(days=days_back)).isoformat() + 'Z'

        self.logger.info(f"Получение всех данных за последние {days_back} дней")

        result = {
            'sales': [],
            'orders': [],
            'stocks': [],
            'financial_report': []
        }

        # Получение продаж
        result['sales'] = self.get_sales(date_from=date_from, flag=1)
        time.sleep(1)  # Небольшая задержка между запросами

        # Получение заказов
        result['orders'] = self.get_orders(date_from=date_from, flag=1)
        time.sleep(1)

        # Получение остатков
        result['stocks'] = self.get_stocks()
        time.sleep(1)

        # Получение детального финансового отчёта (ГЛАВНОЕ для расчёта прибыли!)
        result['financial_report'] = self.get_report_detail_by_period(
            date_from=date_from,
            date_to=date_to
        )

        total_records = (
            len(result['sales']) +
            len(result['orders']) +
            len(result['stocks']) +
            len(result['financial_report'])
        )

        self.logger.info(
            f"Всего получено {total_records} записей: "
            f"продажи={len(result['sales'])}, "
            f"заказы={len(result['orders'])}, "
            f"остатки={len(result['stocks'])}, "
            f"финансовый отчёт={len(result['financial_report'])}"
        )

        return result

    def get_incremental_data(self, last_update: str) -> Dict[str, List[Dict]]:
        """
        Получение инкрементальных данных с последнего обновления

        Args:
            last_update: Дата последнего обновления (ISO формат)

        Returns:
            Словарь с новыми данными
        """
        self.logger.info(f"Получение инкрементальных данных с {last_update}")

        # Конвертация в RFC3339 формат для WB API
        try:
            dt = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
            date_from = dt.isoformat() + 'Z'
        except ValueError:
            self.logger.error(f"Неверный формат даты: {last_update}")
            date_from = (datetime.utcnow() - timedelta(hours=1)).isoformat() + 'Z'

        result = {
            'sales': [],
            'orders': [],
            'stocks': []
        }

        # Получение новых продаж (flag=1 означает данные >= date_from)
        result['sales'] = self.get_sales(date_from=date_from, flag=1)
        time.sleep(1)

        # Получение новых заказов
        result['orders'] = self.get_orders(date_from=date_from, flag=1)
        time.sleep(1)

        # Остатки берем последние
        result['stocks'] = self.get_stocks()

        return result

    def test_connection(self) -> bool:
        """
        Тестирование подключения к API

        Returns:
            True если подключение успешно
        """
        self.logger.info("Тестирование подключения к WB API")

        try:
            # Пытаемся получить данные за последний день
            date_from = (datetime.utcnow() - timedelta(days=1)).isoformat() + 'Z'
            response = self.get_stocks()

            if response is not None:
                self.logger.info("✓ Подключение к WB API успешно")
                return True
            else:
                self.logger.error("✗ Не удалось подключиться к WB API")
                return False

        except Exception as e:
            self.logger.error(f"✗ Ошибка при тестировании подключения: {e}")
            return False

    def close(self):
        """Закрытие сессии"""
        self.session.close()
        self.logger.debug("Сессия WB API закрыта")
