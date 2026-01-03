#!/usr/bin/env python3
"""
Создание тестовых данных для демонстрации WB Analytics Dashboard
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.models import DatabaseManager

def create_test_data():
    """Создание реалистичных тестовых данных"""

    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'wb_analytics.db')
    db = DatabaseManager(db_path)

    print("Создание тестовых данных...")

    # Тестовые товары
    test_products = [
        {
            'nm_id': 123456789,
            'article': 'ART-001',
            'name': 'Футболка мужская',
            'subject': 'Футболки',
            'brand': 'Test Brand',
            'cost_price': 500,
            'wb_commission': 15.0
        },
        {
            'nm_id': 123456790,
            'article': 'ART-002',
            'name': 'Джинсы женские',
            'subject': 'Джинсы',
            'brand': 'Fashion Co',
            'cost_price': 1200,
            'wb_commission': 17.0
        },
        {
            'nm_id': 123456791,
            'article': 'ART-003',
            'name': 'Куртка зимняя',
            'subject': 'Верхняя одежда',
            'brand': 'Winter Wear',
            'cost_price': 3500,
            'wb_commission': 20.0
        },
        {
            'nm_id': 123456792,
            'article': 'ART-004',
            'name': 'Кроссовки спортивные',
            'subject': 'Обувь',
            'brand': 'Sport Line',
            'cost_price': 2000,
            'wb_commission': 18.0
        },
        {
            'nm_id': 123456793,
            'article': 'ART-005',
            'name': 'Платье летнее',
            'subject': 'Платья',
            'brand': 'Summer Style',
            'cost_price': 800,
            'wb_commission': 16.0
        }
    ]

    # Добавляем товары
    for product in test_products:
        db.add_product(
            nm_id=product['nm_id'],
            article=product['article'],
            name=product['name'],
            subject=product['subject'],
            brand=product['brand'],
            cost_price=product['cost_price'],
            wb_commission=product['wb_commission']
        )

    print(f"✓ Создано {len(test_products)} товаров")

    # Генерация продаж и заказов за последние 30 дней
    sales_data = []
    orders_data = []
    financial_data = []

    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    for product in test_products:
        # Для каждого товара создаём от 5 до 30 продаж
        num_sales = random.randint(5, 30)

        for _ in range(num_sales):
            # Случайная дата в диапазоне
            days_ago = random.randint(0, 30)
            sale_date = end_date - timedelta(days=days_ago)

            # Цена продажи (себестоимость * 2-3)
            retail_price = product['cost_price'] * random.uniform(2.0, 3.0)

            # Количество
            quantity = random.randint(1, 3)

            # Комиссия WB
            commission = retail_price * (product['wb_commission'] / 100)

            # Логистика (10-15% от цены)
            logistics = retail_price * random.uniform(0.10, 0.15)

            # Хранение (5-8% от цены)
            storage = retail_price * random.uniform(0.05, 0.08)

            # Штрафы (0-5%)
            penalty = retail_price * random.uniform(0, 0.05) if random.random() < 0.2 else 0

            # К выплате от WB
            to_pay = retail_price - commission - logistics - storage - penalty

            # Продажа (формат WB API)
            sale = {
                'nmId': product['nm_id'],
                'saleID': f'S{random.randint(100000, 999999)}',
                'date': sale_date.isoformat(),
                'lastChangeDate': sale_date.isoformat(),
                'supplierArticle': product['article'],
                'techSize': 'M',
                'barcode': str(random.randint(1000000000000, 9999999999999)),
                'totalPrice': retail_price * quantity,
                'discountPercent': 0,
                'isSupply': 1,
                'isRealization': 0,
                'promoCodeDiscount': 0,
                'warehouseName': 'Коледино',
                'countryName': 'Россия',
                'oblastOkrugName': 'Московская обл',
                'regionName': 'Подольск',
                'incomeID': random.randint(100000, 999999),
                'saleType': 'Продажа',
                'forPay': to_pay * quantity,
                'finishedPrice': retail_price,
                'priceWithDisc': retail_price
            }
            sales_data.append(sale)

            # Финансовый отчёт
            financial = {
                'realizationreport_id': random.randint(1000000, 9999999),
                'rrd_id': random.randint(1000000, 9999999),
                'nm_id': product['nm_id'],
                'sa_name': product['name'],
                'subject_name': product['subject'],
                'brand_name': product['brand'],
                'doc_type_name': 'Продажа',
                'quantity': quantity,
                'retail_price': retail_price,
                'retail_amount': retail_price * quantity,
                'sale_percent': product['wb_commission'],
                'commission_percent': product['wb_commission'],
                'office_name': 'Коледино',
                'supplier_oper_name': 'Продажа',
                'order_dt': sale_date - timedelta(days=random.randint(1, 3)),
                'sale_dt': sale_date,
                'rr_dt': sale_date,
                'ppvz_sales_commission': commission * quantity,
                'ppvz_for_pay': to_pay * quantity,
                'delivery_rub': logistics * 0.7 * quantity,
                'return_amount': logistics * 0.3 * quantity,
                'storage_fee': storage * quantity,
                'penalty': penalty * quantity
            }
            financial_data.append(financial)

    # Добавляем продажи
    if sales_data:
        db.add_sales_batch(sales_data)
        print(f"✓ Создано {len(sales_data)} продаж")

    # Добавляем финансовые отчёты
    if financial_data:
        db.add_financial_report_batch(financial_data)
        print(f"✓ Создано {len(financial_data)} финансовых записей")

    # Добавляем остатки (формат WB API)
    stocks_data = []
    for product in test_products:
        stock = {
            'nmId': product['nm_id'],
            'supplierArticle': product['article'],
            'barcode': str(random.randint(1000000000000, 9999999999999)),
            'quantity': random.randint(10, 100),
            'inWayToClient': random.randint(0, 10),
            'inWayFromClient': random.randint(0, 5),
            'warehouseName': 'Коледино',
            'subject': product['subject'],
            'category': 'Одежда',
            'brand': product['brand'],
            'techSize': 'M',
            'price': product['cost_price'] * 2.5,
            'discount': 0,
            'isSupply': 1,
            'isRealization': 0
        }
        stocks_data.append(stock)

    if stocks_data:
        db.add_stocks_batch(stocks_data)
        print(f"✓ Создано {len(stocks_data)} записей остатков")

    print("\n✅ Тестовые данные успешно созданы!")
    print(f"Период данных: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
    print("\nТеперь можете открыть dashboard и увидеть аналитику!")

if __name__ == '__main__':
    create_test_data()
