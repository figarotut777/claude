"""
Модуль для работы с базой данных SQLite
Хранит историю данных о товарах, продажах и остатках с Wildberries
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager
from pathlib import Path


class DatabaseManager:
    """Менеджер для работы с SQLite базой данных"""

    def __init__(self, db_path: str = "data/wb_analytics.db"):
        """
        Инициализация менеджера БД

        Args:
            db_path: Путь к файлу базы данных
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()

    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для безопасной работы с подключением к БД"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Результаты как словари
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Ошибка работы с БД: {e}")
            raise
        finally:
            conn.close()

    def _init_database(self):
        """Инициализация таблиц базы данных"""
        # Создаём родительскую директорию, если её нет
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Таблица товаров
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nm_id INTEGER UNIQUE NOT NULL,
                    article TEXT NOT NULL,
                    name TEXT NOT NULL,
                    brand TEXT,
                    subject TEXT,
                    category TEXT,
                    cost_price REAL DEFAULT 0,
                    wb_commission_percent REAL DEFAULT 15,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Таблица продаж (снимки данных каждый час)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nm_id INTEGER NOT NULL,
                    sale_id TEXT,
                    date TIMESTAMP NOT NULL,
                    last_change_date TIMESTAMP,
                    supplier_article TEXT,
                    tech_size TEXT,
                    barcode TEXT,
                    total_price REAL NOT NULL,
                    discount_percent REAL DEFAULT 0,
                    is_supply BOOLEAN DEFAULT 0,
                    is_realization BOOLEAN DEFAULT 0,
                    promo_code_discount REAL DEFAULT 0,
                    warehouse_name TEXT,
                    country_name TEXT,
                    oblast_okrug_name TEXT,
                    region_name TEXT,
                    income_id INTEGER,
                    sale_type TEXT,
                    for_pay REAL,
                    finished_price REAL,
                    price_with_disc REAL,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (nm_id) REFERENCES products (nm_id)
                )
            """)

            # Индекс для быстрого поиска продаж по товару и дате
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sales_nm_date
                ON sales(nm_id, date)
            """)

            # Таблица остатков (снимки данных каждый час)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nm_id INTEGER NOT NULL,
                    article TEXT,
                    barcode TEXT,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    in_way_to_client INTEGER DEFAULT 0,
                    in_way_from_client INTEGER DEFAULT 0,
                    warehouse_name TEXT,
                    subject TEXT,
                    category TEXT,
                    brand TEXT,
                    tech_size TEXT,
                    price REAL,
                    discount REAL DEFAULT 0,
                    is_supply BOOLEAN DEFAULT 0,
                    is_realization BOOLEAN DEFAULT 0,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (nm_id) REFERENCES products (nm_id)
                )
            """)

            # Индекс для быстрого поиска остатков
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_stocks_nm_fetched
                ON stocks(nm_id, fetched_at)
            """)

            # Таблица заказов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nm_id INTEGER NOT NULL,
                    order_id TEXT,
                    date TIMESTAMP NOT NULL,
                    last_change_date TIMESTAMP,
                    supplier_article TEXT,
                    tech_size TEXT,
                    barcode TEXT,
                    total_price REAL NOT NULL,
                    discount_percent REAL DEFAULT 0,
                    warehouse_name TEXT,
                    oblast TEXT,
                    income_id INTEGER,
                    is_cancel BOOLEAN DEFAULT 0,
                    cancel_date TIMESTAMP,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (nm_id) REFERENCES products (nm_id)
                )
            """)

            # Индекс для заказов
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_orders_nm_date
                ON orders(nm_id, date)
            """)

            # Таблица детального финансового отчёта (ГЛАВНАЯ для расчёта прибыли!)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS financial_report (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    realizationreport_id INTEGER,
                    rrd_id INTEGER,
                    nm_id INTEGER NOT NULL,
                    sa_name TEXT,
                    subject_name TEXT,
                    brand_name TEXT,
                    ts_name TEXT,
                    barcode TEXT,
                    doc_type_name TEXT,
                    quantity INTEGER DEFAULT 0,
                    retail_price REAL,
                    retail_amount REAL,
                    sale_percent REAL DEFAULT 0,
                    commission_percent REAL DEFAULT 0,
                    office_name TEXT,
                    supplier_oper_name TEXT,
                    order_dt TIMESTAMP,
                    sale_dt TIMESTAMP,
                    rr_dt TIMESTAMP,
                    shk_id TEXT,
                    retail_price_withdisc_rub REAL,
                    delivery_amount REAL DEFAULT 0,
                    return_amount REAL DEFAULT 0,
                    delivery_rub REAL DEFAULT 0,
                    gi_box_type_name TEXT,
                    product_discount_for_report REAL DEFAULT 0,
                    supplier_promo REAL DEFAULT 0,
                    ppvz_spp_prc REAL DEFAULT 0,
                    ppvz_kvw_prc_base REAL DEFAULT 0,
                    ppvz_kvw_prc REAL DEFAULT 0,
                    ppvz_sales_commission REAL DEFAULT 0,
                    ppvz_for_pay REAL DEFAULT 0,
                    ppvz_reward REAL DEFAULT 0,
                    ppvz_vw REAL DEFAULT 0,
                    ppvz_vw_nds REAL DEFAULT 0,
                    ppvz_office_name TEXT,
                    penalty REAL DEFAULT 0,
                    additional_payment REAL DEFAULT 0,
                    storage_fee REAL DEFAULT 0,
                    bonus_type_name TEXT,
                    srid TEXT,
                    date_from DATE,
                    date_to DATE,
                    create_dt TIMESTAMP,
                    currency_name TEXT,
                    suppliercontract_code TEXT,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (nm_id) REFERENCES products (nm_id)
                )
            """)

            # Индекс для финансового отчёта
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_financial_nm_date
                ON financial_report(nm_id, rr_dt)
            """)

            # Таблица для хранения метаданных и конфигурации
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.logger.info("База данных инициализирована успешно")

    def add_product(self, nm_id: int, article: str, name: str,
                   brand: str = None, subject: str = None, category: str = None,
                   cost_price: float = 0, wb_commission: float = 15) -> int:
        """
        Добавление или обновление товара

        Args:
            nm_id: ID товара в WB
            article: Артикул продавца
            name: Название товара
            brand: Бренд
            subject: Предмет
            category: Категория
            cost_price: Себестоимость
            wb_commission: Комиссия WB в процентах

        Returns:
            ID записи в БД
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products (nm_id, article, name, brand, subject, category,
                                    cost_price, wb_commission_percent, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(nm_id) DO UPDATE SET
                    article = excluded.article,
                    name = excluded.name,
                    brand = excluded.brand,
                    subject = excluded.subject,
                    category = excluded.category,
                    cost_price = excluded.cost_price,
                    wb_commission_percent = excluded.wb_commission_percent,
                    updated_at = CURRENT_TIMESTAMP
            """, (nm_id, article, name, brand, subject, category, cost_price, wb_commission))

            return cursor.lastrowid

    def add_sales_batch(self, sales_data: List[Dict]) -> int:
        """
        Массовое добавление данных о продажах

        Args:
            sales_data: Список словарей с данными о продажах

        Returns:
            Количество добавленных записей
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            count = 0

            for sale in sales_data:
                cursor.execute("""
                    INSERT INTO sales (
                        nm_id, sale_id, date, last_change_date, supplier_article,
                        tech_size, barcode, total_price, discount_percent, is_supply,
                        is_realization, promo_code_discount, warehouse_name, country_name,
                        oblast_okrug_name, region_name, income_id, sale_type, for_pay,
                        finished_price, price_with_disc
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    sale.get('nmId'),
                    sale.get('saleID'),
                    sale.get('date'),
                    sale.get('lastChangeDate'),
                    sale.get('supplierArticle'),
                    sale.get('techSize'),
                    sale.get('barcode'),
                    sale.get('totalPrice', 0),
                    sale.get('discountPercent', 0),
                    sale.get('isSupply', 0),
                    sale.get('isRealization', 0),
                    sale.get('promoCodeDiscount', 0),
                    sale.get('warehouseName'),
                    sale.get('countryName'),
                    sale.get('oblastOkrugName'),
                    sale.get('regionName'),
                    sale.get('incomeID'),
                    sale.get('saleType'),
                    sale.get('forPay'),
                    sale.get('finishedPrice'),
                    sale.get('priceWithDisc')
                ))
                count += 1

            self.logger.info(f"Добавлено {count} записей о продажах")
            return count

    def add_stocks_batch(self, stocks_data: List[Dict]) -> int:
        """
        Массовое добавление данных об остатках

        Args:
            stocks_data: Список словарей с данными об остатках

        Returns:
            Количество добавленных записей
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            count = 0

            for stock in stocks_data:
                cursor.execute("""
                    INSERT INTO stocks (
                        nm_id, article, barcode, quantity, in_way_to_client,
                        in_way_from_client, warehouse_name, subject, category,
                        brand, tech_size, price, discount, is_supply, is_realization
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    stock.get('nmId'),
                    stock.get('supplierArticle'),
                    stock.get('barcode'),
                    stock.get('quantity', 0),
                    stock.get('inWayToClient', 0),
                    stock.get('inWayFromClient', 0),
                    stock.get('warehouseName'),
                    stock.get('subject'),
                    stock.get('category'),
                    stock.get('brand'),
                    stock.get('techSize'),
                    stock.get('Price'),
                    stock.get('Discount', 0),
                    stock.get('isSupply', 0),
                    stock.get('isRealization', 0)
                ))
                count += 1

            self.logger.info(f"Добавлено {count} записей об остатках")
            return count

    def add_orders_batch(self, orders_data: List[Dict]) -> int:
        """
        Массовое добавление данных о заказах

        Args:
            orders_data: Список словарей с данными о заказах

        Returns:
            Количество добавленных записей
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            count = 0

            for order in orders_data:
                cursor.execute("""
                    INSERT INTO orders (
                        nm_id, order_id, date, last_change_date, supplier_article,
                        tech_size, barcode, total_price, discount_percent,
                        warehouse_name, oblast, income_id, is_cancel, cancel_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    order.get('nmId'),
                    order.get('odid'),
                    order.get('date'),
                    order.get('lastChangeDate'),
                    order.get('supplierArticle'),
                    order.get('techSize'),
                    order.get('barcode'),
                    order.get('totalPrice', 0),
                    order.get('discountPercent', 0),
                    order.get('warehouseName'),
                    order.get('oblast'),
                    order.get('incomeID'),
                    order.get('isCancel', 0),
                    order.get('cancelDate')
                ))
                count += 1

            self.logger.info(f"Добавлено {count} записей о заказах")
            return count

    def add_financial_report_batch(self, report_data: List[Dict]) -> int:
        """
        Массовое добавление данных финансового отчёта

        Args:
            report_data: Список словарей с данными финансового отчёта

        Returns:
            Количество добавленных записей
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            count = 0

            for item in report_data:
                cursor.execute("""
                    INSERT INTO financial_report (
                        realizationreport_id, rrd_id, nm_id, sa_name,
                        subject_name, brand_name, ts_name, barcode,
                        doc_type_name, quantity, retail_price, retail_amount,
                        sale_percent, commission_percent, office_name,
                        supplier_oper_name, order_dt, sale_dt, rr_dt,
                        shk_id, retail_price_withdisc_rub, delivery_amount,
                        return_amount, delivery_rub, gi_box_type_name,
                        product_discount_for_report, supplier_promo,
                        ppvz_spp_prc, ppvz_kvw_prc_base, ppvz_kvw_prc,
                        ppvz_sales_commission, ppvz_for_pay, ppvz_reward,
                        ppvz_vw, ppvz_vw_nds, ppvz_office_name,
                        penalty, additional_payment, storage_fee,
                        bonus_type_name, srid, date_from, date_to,
                        create_dt, currency_name, suppliercontract_code
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.get('realizationreport_id'),
                    item.get('rrd_id'),
                    item.get('nm_id'),
                    item.get('sa_name'),
                    item.get('subject_name'),
                    item.get('brand_name'),
                    item.get('ts_name'),
                    item.get('barcode'),
                    item.get('doc_type_name'),
                    item.get('quantity', 0),
                    item.get('retail_price'),
                    item.get('retail_amount'),
                    item.get('sale_percent', 0),
                    item.get('commission_percent', 0),
                    item.get('office_name'),
                    item.get('supplier_oper_name'),
                    item.get('order_dt'),
                    item.get('sale_dt'),
                    item.get('rr_dt'),
                    item.get('shk_id'),
                    item.get('retail_price_withdisc_rub'),
                    item.get('delivery_amount', 0),
                    item.get('return_amount', 0),
                    item.get('delivery_rub', 0),
                    item.get('gi_box_type_name'),
                    item.get('product_discount_for_report', 0),
                    item.get('supplier_promo', 0),
                    item.get('ppvz_spp_prc', 0),
                    item.get('ppvz_kvw_prc_base', 0),
                    item.get('ppvz_kvw_prc', 0),
                    item.get('ppvz_sales_commission', 0),
                    item.get('ppvz_for_pay', 0),
                    item.get('ppvz_reward', 0),
                    item.get('ppvz_vw', 0),
                    item.get('ppvz_vw_nds', 0),
                    item.get('ppvz_office_name'),
                    item.get('penalty', 0),
                    item.get('additional_payment', 0),
                    item.get('storage_fee', 0),
                    item.get('bonus_type_name'),
                    item.get('srid'),
                    item.get('date_from'),
                    item.get('date_to'),
                    item.get('create_dt'),
                    item.get('currency_name'),
                    item.get('suppliercontract_code')
                ))
                count += 1

            self.logger.info(f"Добавлено {count} записей финансового отчёта")
            return count

    def get_products(self) -> List[Dict]:
        """Получение списка всех товаров"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products ORDER BY nm_id")
            return [dict(row) for row in cursor.fetchall()]

    def get_product_by_nm_id(self, nm_id: int) -> Optional[Dict]:
        """Получение товара по nm_id"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE nm_id = ?", (nm_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_product_settings(self, nm_id: int, cost_price: float = None,
                               wb_commission: float = None) -> bool:
        """
        Обновление настроек товара (себестоимость, комиссия)

        Args:
            nm_id: ID товара
            cost_price: Новая себестоимость
            wb_commission: Новая комиссия WB

        Returns:
            True если обновление прошло успешно
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            updates = []
            params = []

            if cost_price is not None:
                updates.append("cost_price = ?")
                params.append(cost_price)

            if wb_commission is not None:
                updates.append("wb_commission_percent = ?")
                params.append(wb_commission)

            if not updates:
                return False

            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(nm_id)

            query = f"UPDATE products SET {', '.join(updates)} WHERE nm_id = ?"
            cursor.execute(query, params)

            return cursor.rowcount > 0

    def get_sales_for_period(self, start_date: str, end_date: str,
                            nm_id: int = None) -> List[Dict]:
        """
        Получение продаж за период

        Args:
            start_date: Начало периода (ISO формат)
            end_date: Конец периода (ISO формат)
            nm_id: ID товара (опционально, для фильтрации)

        Returns:
            Список продаж
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if nm_id:
                cursor.execute("""
                    SELECT * FROM sales
                    WHERE date BETWEEN ? AND ? AND nm_id = ?
                    ORDER BY date
                """, (start_date, end_date, nm_id))
            else:
                cursor.execute("""
                    SELECT * FROM sales
                    WHERE date BETWEEN ? AND ?
                    ORDER BY date
                """, (start_date, end_date))

            return [dict(row) for row in cursor.fetchall()]

    def get_orders_for_period(self, start_date: str, end_date: str,
                             nm_id: int = None) -> List[Dict]:
        """Получение заказов за период"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if nm_id:
                cursor.execute("""
                    SELECT * FROM orders
                    WHERE date BETWEEN ? AND ? AND nm_id = ?
                    ORDER BY date
                """, (start_date, end_date, nm_id))
            else:
                cursor.execute("""
                    SELECT * FROM orders
                    WHERE date BETWEEN ? AND ?
                    ORDER BY date
                """, (start_date, end_date))

            return [dict(row) for row in cursor.fetchall()]

    def get_latest_stocks(self) -> List[Dict]:
        """Получение последних данных об остатках"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s1.* FROM stocks s1
                INNER JOIN (
                    SELECT nm_id, MAX(fetched_at) as max_fetched
                    FROM stocks
                    GROUP BY nm_id
                ) s2 ON s1.nm_id = s2.nm_id AND s1.fetched_at = s2.max_fetched
                ORDER BY s1.nm_id
            """)

            return [dict(row) for row in cursor.fetchall()]

    def get_financial_report_for_period(self, start_date: str, end_date: str,
                                        nm_id: int = None) -> List[Dict]:
        """
        Получение финансового отчёта за период

        Args:
            start_date: Начало периода (ISO формат)
            end_date: Конец периода (ISO формат)
            nm_id: ID товара (опционально)

        Returns:
            Список записей финансового отчёта
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if nm_id:
                cursor.execute("""
                    SELECT * FROM financial_report
                    WHERE rr_dt BETWEEN ? AND ? AND nm_id = ?
                    ORDER BY rr_dt
                """, (start_date, end_date, nm_id))
            else:
                cursor.execute("""
                    SELECT * FROM financial_report
                    WHERE rr_dt BETWEEN ? AND ?
                    ORDER BY rr_dt
                """, (start_date, end_date))

            return [dict(row) for row in cursor.fetchall()]

    def set_metadata(self, key: str, value: str):
        """Сохранение метаданных"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO metadata (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
            """, (key, value))

    def get_metadata(self, key: str) -> Optional[str]:
        """Получение метаданных"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM metadata WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row['value'] if row else None

    def clean_old_data(self, days_to_keep: int = 90):
        """
        Очистка старых данных (старше указанного количества дней)

        Args:
            days_to_keep: Количество дней для хранения
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Удаление старых продаж
            cursor.execute("""
                DELETE FROM sales
                WHERE date < datetime('now', '-' || ? || ' days')
            """, (days_to_keep,))
            sales_deleted = cursor.rowcount

            # Удаление старых остатков
            cursor.execute("""
                DELETE FROM stocks
                WHERE fetched_at < datetime('now', '-' || ? || ' days')
            """, (days_to_keep,))
            stocks_deleted = cursor.rowcount

            # Удаление старых заказов
            cursor.execute("""
                DELETE FROM orders
                WHERE date < datetime('now', '-' || ? || ' days')
            """, (days_to_keep,))
            orders_deleted = cursor.rowcount

            self.logger.info(
                f"Удалено старых записей: продажи={sales_deleted}, "
                f"остатки={stocks_deleted}, заказы={orders_deleted}"
            )
