#!/usr/bin/env python3
"""
Тестирование прямых запросов к WB API
"""
import sys
import os
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.wb_client import WildberriesAPIClient
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

api_key = os.getenv('WB_API_KEY')

if not api_key:
    print("❌ WB_API_KEY не найден в .env файле!")
    sys.exit(1)

print("=" * 70)
print("Тестирование WB API")
print("=" * 70)

client = WildberriesAPIClient(api_key)

# Тест 1: Продажи за последние 30 дней
print("\n1️⃣ Тест: Продажи за последние 30 дней")
date_from = (datetime.utcnow() - timedelta(days=30)).isoformat() + 'Z'
sales = client.get_sales(date_from=date_from, flag=1)

print(f"   Получено записей: {len(sales)}")
if sales:
    print(f"   Пример первой записи:")
    print(json.dumps(sales[0], indent=2, ensure_ascii=False))
else:
    print("   ℹ️  Нет продаж за последние 30 дней")

# Тест 2: Остатки
print("\n2️⃣ Тест: Остатки товаров")
stocks = client.get_stocks()

print(f"   Получено записей: {len(stocks)}")
if stocks:
    print(f"   Пример первой записи:")
    print(json.dumps(stocks[0], indent=2, ensure_ascii=False))
else:
    print("   ℹ️  Нет остатков")

# Тест 3: Финансовый отчёт
print("\n3️⃣ Тест: Финансовый отчёт (reportDetailByPeriod v5)")
date_to = datetime.utcnow().strftime('%Y-%m-%d')
date_from_report = (datetime.utcnow() - timedelta(days=30)).isoformat() + 'Z'

financial = client.get_report_detail_by_period(
    date_from=date_from_report,
    date_to=date_to,
    limit=10
)

print(f"   Получено записей: {len(financial)}")
if financial:
    print(f"   Пример первой записи:")
    print(json.dumps(financial[0], indent=2, ensure_ascii=False))

    # Проверка на ненулевые суммы
    non_zero = [f for f in financial if f.get('retail_amount', 0) > 0 or f.get('ppvz_for_pay', 0) > 0]
    print(f"\n   📊 Записей с ненулевыми суммами: {len(non_zero)} из {len(financial)}")

    if non_zero:
        print("   Пример записи с суммой:")
        print(json.dumps(non_zero[0], indent=2, ensure_ascii=False))
else:
    print("   ℹ️  Нет финансовых записей")

# Тест 4: Заказы
print("\n4️⃣ Тест: Заказы за последние 30 дней")
orders = client.get_orders(date_from=date_from, flag=1)

print(f"   Получено записей: {len(orders)}")
if orders:
    print(f"   Пример первой записи:")
    print(json.dumps(orders[0], indent=2, ensure_ascii=False))
else:
    print("   ℹ️  Нет заказов за последние 30 дней")

print("\n" + "=" * 70)
print("📋 Резюме:")
print(f"   Продажи: {len(sales)}")
print(f"   Заказы: {len(orders)}")
print(f"   Остатки: {len(stocks)}")
print(f"   Финансовый отчёт: {len(financial)}")
print("=" * 70)
