#!/usr/bin/env python3
"""
Создание демонстрационных данных для тестирования дашборда
"""

import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random

# Добавление корневой директории в путь
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

DB_PATH = ROOT_DIR / 'data' / 'wb_analytics.db'


def create_demo_data():
    """Создание демонстрационных данных"""
    print("\n" + "=" * 70)
    print("  Создание демонстрационных данных")
    print("=" * 70 + "\n")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Очистка существующих данных
    print("Очистка существующих данных...")
    cursor.execute("DELETE FROM sales")
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM stocks")
    cursor.execute("DELETE FROM products")
    cursor.execute("DELETE FROM financial_report")
    cursor.execute("DELETE FROM sku_cost_price")
    conn.commit()
    print("✓ Данные очищены\n")

    # Создание тестовых товаров
    print("Создание тестовых товаров...")
    products = [
        (123456789, 'ART-001', 'Футболка базовая', 'TestBrand', 'Одежда', 'Футболки'),
        (123456790, 'ART-002', 'Джинсы классические', 'TestBrand', 'Одежда', 'Джинсы'),
        (123456791, 'ART-003', 'Кроссовки спортивные', 'SportBrand', 'Обувь', 'Кроссовки'),
        (123456792, 'ART-004', 'Рюкзак городской', 'BagBrand', 'Аксессуары', 'Рюкзаки'),
        (123456793, 'ART-005', 'Худи оверсайз', 'TestBrand', 'Одежда', 'Толстовки'),
    ]

    for nm_id, article, name, brand, category, subject in products:
        cursor.execute("""
            INSERT INTO products (nm_id, article, name, brand, category, subject)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nm_id, article, name, brand, category, subject))

    print(f"✓ Создано {len(products)} товаров\n")

    # Создание себестоимости для товаров
    print("Установка себестоимости...")
    cost_prices = [500, 800, 1200, 600, 700]
    for i, (nm_id, _, _, _, _, _) in enumerate(products):
        cursor.execute("""
            INSERT INTO sku_cost_price (nm_id, cost_price, valid_from)
            VALUES (?, ?, ?)
        """, (nm_id, cost_prices[i], '2025-01-01'))

    print(f"✓ Установлена себестоимость для {len(products)} товаров\n")

    # Создание продаж за последние 30 дней
    print("Создание продаж...")
    now = datetime.now()
    sales_count = 0

    for days_ago in range(30):
        date = now - timedelta(days=days_ago)
        date_str = date.strftime('%Y-%m-%d')

        for nm_id, _, _, _, _, _ in products:
            # Случайное количество продаж (0-5 в день)
            num_sales = random.randint(0, 5)

            for _ in range(num_sales):
                price = random.randint(1000, 3000)

                cursor.execute("""
                    INSERT INTO sales (
                        nm_id, date, sale_id, quantity, price_with_disc,
                        finished_price, for_pay, finished_price_total
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    nm_id,
                    date_str,
                    f"S{nm_id}{days_ago}{_}",
                    1,
                    price,
                    price,
                    int(price * 0.85),  # 15% комиссия
                    price
                ))
                sales_count += 1

    print(f"✓ Создано {sales_count} продаж\n")

    # Создание финансового отчёта
    print("Создание финансового отчёта...")
    report_count = 0

    for days_ago in range(30):
        date = now - timedelta(days=days_ago)
        date_str = date.strftime('%Y-%m-%d')

        for nm_id, _, _, _, _, _ in products:
            # Случайные финансовые данные
            retail_amount = random.randint(1000, 5000)

            cursor.execute("""
                INSERT INTO financial_report (
                    nm_id, date, rrd_id, retail_amount, ppvz_for_pay,
                    acquiring_fee, delivery_rub, penalty, storage_fee,
                    acceptance, commission
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                nm_id,
                date_str,
                f"R{nm_id}{days_ago}",
                retail_amount,
                int(retail_amount * 0.85),  # К выплате
                int(retail_amount * 0.02),  # Эквайринг
                int(retail_amount * 0.05),  # Логистика
                random.randint(0, 100),      # Штрафы
                random.randint(10, 50),      # Хранение
                random.randint(5, 20),       # Приёмка
                int(retail_amount * 0.15)    # Комиссия WB
            ))
            report_count += 1

    print(f"✓ Создано {report_count} записей финансового отчёта\n")

    # Создание остатков
    print("Создание остатков...")
    for nm_id, _, _, _, _, _ in products:
        stock_qty = random.randint(10, 100)

        cursor.execute("""
            INSERT INTO stocks (
                nm_id, warehouse_name, quantity, in_way_to_client,
                in_way_from_client, quantity_full, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            nm_id,
            'Склад Москва',
            stock_qty,
            random.randint(0, 10),
            random.randint(0, 5),
            stock_qty,
            datetime.now().isoformat()
        ))

    print(f"✓ Создано {len(products)} записей остатков\n")

    # Сохранение изменений
    conn.commit()
    conn.close()

    print("=" * 70)
    print("✅ Демонстрационные данные успешно созданы!")
    print("=" * 70)
    print(f"\nСтатистика:")
    print(f"  • Товаров: {len(products)}")
    print(f"  • Продаж: {sales_count}")
    print(f"  • Финансовых записей: {report_count}")
    print(f"  • Остатков: {len(products)}")
    print(f"\nТеперь запустите сервер:")
    print(f"  python scripts/start_server.py")
    print(f"\nИ откройте: http://localhost:8080\n")


if __name__ == '__main__':
    create_demo_data()
