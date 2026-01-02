"""
Сервис синхронизации данных из Wildberries API в базу данных
Обеспечивает регулярное обновление данных о продажах, заказах и остатках
"""

import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

# Добавление корневой директории в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.api.wb_client import WildberriesAPIClient
from src.database.models import DatabaseManager


class DataSyncService:
    """Сервис для синхронизации данных WB с локальной БД"""

    def __init__(self, api_key: str, db_path: str = "data/wb_analytics.db"):
        """
        Инициализация сервиса синхронизации

        Args:
            api_key: API ключ Wildberries
            db_path: Путь к базе данных SQLite
        """
        self.logger = logging.getLogger(__name__)
        self.wb_client = WildberriesAPIClient(api_key=api_key)
        self.db = DatabaseManager(db_path=db_path)

    def sync_all_data(self, days_back: int = 30) -> Dict[str, int]:
        """
        Полная синхронизация всех данных за указанный период

        Args:
            days_back: Количество дней истории для загрузки

        Returns:
            Словарь с количеством синхронизированных записей
        """
        self.logger.info(f"Начало полной синхронизации данных за {days_back} дней")

        stats = {
            'sales': 0,
            'orders': 0,
            'stocks': 0,
            'products': 0
        }

        try:
            # Получение данных из WB API
            data = self.wb_client.get_all_data_for_period(days_back=days_back)

            # Синхронизация продаж
            if data['sales']:
                self._sync_products_from_sales(data['sales'])
                stats['sales'] = self.db.add_sales_batch(data['sales'])

            # Синхронизация заказов
            if data['orders']:
                self._sync_products_from_orders(data['orders'])
                stats['orders'] = self.db.add_orders_batch(data['orders'])

            # Синхронизация остатков
            if data['stocks']:
                self._sync_products_from_stocks(data['stocks'])
                stats['stocks'] = self.db.add_stocks_batch(data['stocks'])

            # Синхронизация финансового отчёта (ГЛАВНОЕ!)
            if data['financial_report']:
                self._sync_products_from_financial_report(data['financial_report'])
                stats['financial_report'] = self.db.add_financial_report_batch(data['financial_report'])
                self.logger.info(f"Синхронизировано {stats['financial_report']} записей финансового отчёта")

            # Обновление времени последней синхронизации
            self.db.set_metadata('last_full_sync', datetime.utcnow().isoformat())

            self.logger.info(
                f"Полная синхронизация завершена: "
                f"продажи={stats['sales']}, заказы={stats['orders']}, "
                f"остатки={stats['stocks']}, "
                f"финансовый отчёт={stats.get('financial_report', 0)}"
            )

            return stats

        except Exception as e:
            self.logger.error(f"Ошибка при полной синхронизации: {e}", exc_info=True)
            raise

    def sync_incremental(self) -> Dict[str, int]:
        """
        Инкрементальная синхронизация - загружает только новые данные
        с момента последнего обновления

        Returns:
            Словарь с количеством синхронизированных записей
        """
        self.logger.info("Начало инкрементальной синхронизации")

        stats = {
            'sales': 0,
            'orders': 0,
            'stocks': 0
        }

        try:
            # Получение времени последнего обновления
            last_update = self.db.get_metadata('last_incremental_sync')

            if not last_update:
                # Если это первая синхронизация, берем данные за последний час
                last_update = (datetime.utcnow() - timedelta(hours=1)).isoformat()
                self.logger.info("Первая синхронизация, загружаем данные за последний час")

            # Получение новых данных
            data = self.wb_client.get_incremental_data(last_update=last_update)

            # Синхронизация продаж
            if data['sales']:
                self._sync_products_from_sales(data['sales'])
                stats['sales'] = self.db.add_sales_batch(data['sales'])

            # Синхронизация заказов
            if data['orders']:
                self._sync_products_from_orders(data['orders'])
                stats['orders'] = self.db.add_orders_batch(data['orders'])

            # Синхронизация остатков
            if data['stocks']:
                self._sync_products_from_stocks(data['stocks'])
                stats['stocks'] = self.db.add_stocks_batch(data['stocks'])

            # Обновление времени последней синхронизации
            current_time = datetime.utcnow().isoformat()
            self.db.set_metadata('last_incremental_sync', current_time)

            self.logger.info(
                f"Инкрементальная синхронизация завершена: "
                f"продажи={stats['sales']}, заказы={stats['orders']}, "
                f"остатки={stats['stocks']}"
            )

            return stats

        except Exception as e:
            self.logger.error(f"Ошибка при инкрементальной синхронизации: {e}", exc_info=True)
            raise

    def _sync_products_from_sales(self, sales: List[Dict]):
        """
        Синхронизация товаров из данных о продажах

        Args:
            sales: Список продаж
        """
        # Извлечение уникальных товаров из продаж
        products_map = {}

        for sale in sales:
            nm_id = sale.get('nmId')
            if nm_id and nm_id not in products_map:
                products_map[nm_id] = {
                    'nm_id': nm_id,
                    'article': sale.get('supplierArticle', ''),
                    'name': sale.get('subject', f'Товар {nm_id}'),
                    'brand': sale.get('brand', ''),
                    'subject': sale.get('subject', ''),
                    'category': sale.get('category', '')
                }

        # Добавление товаров в БД
        for product in products_map.values():
            try:
                self.db.add_product(
                    nm_id=product['nm_id'],
                    article=product['article'],
                    name=product['name'],
                    brand=product.get('brand'),
                    subject=product.get('subject'),
                    category=product.get('category')
                )
            except Exception as e:
                self.logger.warning(f"Не удалось добавить товар {product['nm_id']}: {e}")

        self.logger.debug(f"Синхронизировано {len(products_map)} товаров из продаж")

    def _sync_products_from_orders(self, orders: List[Dict]):
        """
        Синхронизация товаров из данных о заказах

        Args:
            orders: Список заказов
        """
        products_map = {}

        for order in orders:
            nm_id = order.get('nmId')
            if nm_id and nm_id not in products_map:
                products_map[nm_id] = {
                    'nm_id': nm_id,
                    'article': order.get('supplierArticle', ''),
                    'name': order.get('subject', f'Товар {nm_id}'),
                    'brand': order.get('brand', ''),
                    'subject': order.get('subject', ''),
                    'category': order.get('category', '')
                }

        # Добавление товаров в БД
        for product in products_map.values():
            try:
                self.db.add_product(
                    nm_id=product['nm_id'],
                    article=product['article'],
                    name=product['name'],
                    brand=product.get('brand'),
                    subject=product.get('subject'),
                    category=product.get('category')
                )
            except Exception as e:
                self.logger.warning(f"Не удалось добавить товар {product['nm_id']}: {e}")

        self.logger.debug(f"Синхронизировано {len(products_map)} товаров из заказов")

    def _sync_products_from_stocks(self, stocks: List[Dict]):
        """
        Синхронизация товаров из данных об остатках

        Args:
            stocks: Список остатков
        """
        products_map = {}

        for stock in stocks:
            nm_id = stock.get('nmId')
            if nm_id and nm_id not in products_map:
                products_map[nm_id] = {
                    'nm_id': nm_id,
                    'article': stock.get('supplierArticle', ''),
                    'name': stock.get('subject', f'Товар {nm_id}'),
                    'brand': stock.get('brand', ''),
                    'subject': stock.get('subject', ''),
                    'category': stock.get('category', '')
                }

        # Добавление товаров в БД
        for product in products_map.values():
            try:
                self.db.add_product(
                    nm_id=product['nm_id'],
                    article=product['article'],
                    name=product['name'],
                    brand=product.get('brand'),
                    subject=product.get('subject'),
                    category=product.get('category')
                )
            except Exception as e:
                self.logger.warning(f"Не удалось добавить товар {product['nm_id']}: {e}")

        self.logger.debug(f"Синхронизировано {len(products_map)} товаров из остатков")

    def _sync_products_from_financial_report(self, report: List[Dict]):
        """
        Синхронизация товаров из финансового отчёта

        Args:
            report: Список записей финансового отчёта
        """
        products_map = {}

        for item in report:
            nm_id = item.get('nm_id')
            if nm_id and nm_id not in products_map:
                products_map[nm_id] = {
                    'nm_id': nm_id,
                    'article': item.get('sa_name', ''),
                    'name': item.get('subject_name', f'Товар {nm_id}'),
                    'brand': item.get('brand_name', ''),
                    'subject': item.get('subject_name', ''),
                    'category': ''
                }

        # Добавление товаров в БД
        for product in products_map.values():
            try:
                self.db.add_product(
                    nm_id=product['nm_id'],
                    article=product['article'],
                    name=product['name'],
                    brand=product.get('brand'),
                    subject=product.get('subject'),
                    category=product.get('category')
                )
            except Exception as e:
                self.logger.warning(f"Не удалось добавить товар {product['nm_id']}: {e}")

        self.logger.debug(f"Синхронизировано {len(products_map)} товаров из финансового отчёта")

    def update_product_settings(self, products_config: List[Dict]):
        """
        Обновление настроек товаров (себестоимость, комиссия)

        Args:
            products_config: Список конфигураций товаров
                [{
                    'nm_id': 123456,
                    'cost_price': 500.0,
                    'wb_commission': 15.0
                }, ...]
        """
        self.logger.info(f"Обновление настроек для {len(products_config)} товаров")

        for config in products_config:
            try:
                nm_id = config.get('nm_id')
                cost_price = config.get('cost_price')
                wb_commission = config.get('wb_commission')

                if nm_id:
                    success = self.db.update_product_settings(
                        nm_id=nm_id,
                        cost_price=cost_price,
                        wb_commission=wb_commission
                    )

                    if success:
                        self.logger.debug(f"Обновлены настройки товара {nm_id}")
                    else:
                        self.logger.warning(f"Товар {nm_id} не найден в БД")

            except Exception as e:
                self.logger.error(f"Ошибка при обновлении настроек товара: {e}")

    def test_api_connection(self) -> bool:
        """
        Тестирование подключения к WB API

        Returns:
            True если подключение успешно
        """
        return self.wb_client.test_connection()

    def cleanup_old_data(self, days_to_keep: int = 90):
        """
        Очистка старых данных из БД

        Args:
            days_to_keep: Количество дней для хранения
        """
        self.logger.info(f"Очистка данных старше {days_to_keep} дней")
        try:
            self.db.clean_old_data(days_to_keep=days_to_keep)
            self.logger.info("Очистка завершена успешно")
        except Exception as e:
            self.logger.error(f"Ошибка при очистке данных: {e}")

    def get_sync_status(self) -> Dict:
        """
        Получение статуса синхронизации

        Returns:
            Словарь с информацией о последних синхронизациях
        """
        return {
            'last_full_sync': self.db.get_metadata('last_full_sync'),
            'last_incremental_sync': self.db.get_metadata('last_incremental_sync'),
            'total_products': len(self.db.get_products())
        }

    def close(self):
        """Закрытие соединений"""
        self.wb_client.close()
        self.logger.info("Сервис синхронизации остановлен")
