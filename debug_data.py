#!/usr/bin/env python3
"""
Скрипт для диагностики данных в БД и вывода API
"""
import sys
import json
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent / 'wb_analytics'))

from src.services.analytics import AnalyticsService
from src.database.models import DatabaseManager
from datetime import datetime, timedelta

DB_PATH = 'wb_analytics/data/wb_analytics.db'

print('=' * 100)
print('ДИАГНОСТИКА ДАННЫХ WB ANALYTICS')
print('=' * 100)

# 1. Проверка БД
print('\n1. ПРОВЕРКА БАЗЫ ДАННЫХ:')
db = DatabaseManager(DB_PATH)
products = db.get_products()
print(f'   Товаров в products: {len(products)}')

# 2. Проверка financial_report
import sqlite3
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM financial_report')
fr_count = cursor.fetchone()[0]
print(f'   Записей в financial_report: {fr_count}')

if fr_count > 0:
    cursor.execute('SELECT MIN(rr_dt), MAX(rr_dt) FROM financial_report')
    min_date, max_date = cursor.fetchone()
    print(f'   Даты: {min_date} → {max_date}')

    # Пример записей
    print('\n2. ПРИМЕРЫ ДАННЫХ ИЗ FINANCIAL_REPORT:')
    cursor.execute('''
        SELECT rr_dt, doc_type_name, nm_id, quantity, retail_amount,
               ppvz_for_pay, return_amount, ppvz_sales_commission
        FROM financial_report
        LIMIT 10
    ''')

    rows = cursor.fetchall()
    if rows:
        print(f'   {"Дата":<20} {"Тип":<12} {"nm_id":<10} {"qty":<5} {"retail":<10} {"for_pay":<10} {"return":<10} {"comm":<10}')
        print('   ' + '-' * 95)
        for row in rows:
            print(f'   {row[0]:<20} {row[1] or "NULL":<12} {row[2]:<10} {row[3]:<5} {row[4] or 0:<10.2f} {row[5] or 0:<10.2f} {row[6] or 0:<10.2f} {row[7] or 0:<10.2f}')

conn.close()

# 3. Вызов API методов
if fr_count > 0:
    print('\n3. ВЫЗОВ ANALYTICS API:')
    analytics = AnalyticsService(DB_PATH)

    periods = ['today', 'week', 'month']
    for period in periods:
        try:
            data = analytics.get_dashboard_data(period=period)
            products_count = len(data.get('products_summary', []))
            sales_qty = data.get('metrics', {}).get('sales', {}).get('quantity', 0)

            print(f'   {period:10} → товаров: {products_count:3}, продано: {sales_qty:4}')

            if products_count > 0 and period == 'month':
                print('\n4. ПРИМЕР ТОВАРА ИЗ products_summary (period=month):')
                product = data['products_summary'][0]
                print(json.dumps(product, indent=4, ensure_ascii=False))
                break

        except Exception as e:
            print(f'   {period:10} → ОШИБКА: {e}')
else:
    print('\n❌ БАЗА ДАННЫХ ПУСТАЯ! Нужно запустить синхронизацию.')
    print('   Команда: python3 wb_analytics/scripts/sync_data.py')

print('\n' + '=' * 100)
