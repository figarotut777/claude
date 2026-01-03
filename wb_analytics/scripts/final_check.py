#!/usr/bin/env python3
"""
Финальная проверка данных - показывает реальные цифры из БД
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

db_path = ROOT_DIR / 'data' / 'wb_analytics.db'

if not db_path.exists():
    print(f"❌ База данных не найдена: {db_path}")
    sys.exit(1)

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 70)
print("ФИНАЛЬНАЯ ПРОВЕРКА ДАННЫХ")
print("=" * 70)

# 1. Товары с фотографиями
print("\n1. ТОВАРЫ:")
cursor.execute("SELECT COUNT(*) as cnt FROM products")
print(f"   Всего: {cursor.fetchone()['cnt']}")

cursor.execute("""
    SELECT nm_id, name, brand, article, image_url
    FROM products
    LIMIT 5
""")
print("\n   Первые 5 товаров:")
for p in cursor.fetchall():
    has_image = "✓" if p['image_url'] else "✗"
    print(f"   [{has_image}] {p['name']} ({p['brand']}) - {p['article']} [nm_id: {p['nm_id']}]")

# 2. Финансовый отчет - ГЛАВНЫЙ ИСТОЧНИК ДАННЫХ
print("\n2. ФИНАНСОВЫЙ ОТЧЁТ (главный источник):")
cursor.execute("SELECT COUNT(*) as cnt FROM financial_report")
total_fr = cursor.fetchone()['cnt']
print(f"   Всего записей: {total_fr}")

if total_fr > 0:
    # Суммы
    cursor.execute("""
        SELECT
            SUM(retail_amount) as total_revenue,
            SUM(ppvz_for_pay) as total_to_pay,
            SUM(storage_fee) as total_storage,
            SUM(penalty) as total_penalty,
            SUM(ppvz_sales_commission) as total_commission,
            SUM(delivery_rub) as total_delivery
        FROM financial_report
    """)
    sums = cursor.fetchone()

    print(f"\n   📊 СУММЫ ЗА ВСЁ ВРЕМЯ:")
    print(f"   💰 Выручка: {sums['total_revenue']:.2f} ₽")
    print(f"   💳 К выплате от WB: {sums['total_to_pay']:.2f} ₽")
    print(f"   🏪 Комиссия WB: {sums['total_commission']:.2f} ₽")
    print(f"   📦 Логистика: {sums['total_delivery']:.2f} ₽")
    print(f"   🏭 Хранение: {sums['total_storage']:.2f} ₽")
    print(f"   ⚠️  Штрафы: {sums['total_penalty']:.2f} ₽")

    # Последние операции
    cursor.execute("""
        SELECT
            rr_dt,
            doc_type_name,
            supplier_oper_name,
            quantity,
            retail_amount,
            ppvz_for_pay,
            storage_fee,
            penalty
        FROM financial_report
        ORDER BY rr_dt DESC
        LIMIT 10
    """)
    print(f"\n   📋 Последние 10 операций:")
    for row in cursor.fetchall():
        doc = row['doc_type_name'] or '(без типа)'
        oper = row['supplier_oper_name'] or '-'
        date = row['rr_dt'][:10] if row['rr_dt'] else '-'
        print(f"   {date}: {doc:15s} | {oper:20s} | qty={row['quantity']:3d} | "
              f"revenue={row['retail_amount'] or 0:8.2f} | to_pay={row['ppvz_for_pay'] or 0:8.2f}")

# 3. Продажи (дополнительный источник)
print("\n3. ПРОДАЖИ (sales):")
cursor.execute("SELECT COUNT(*) as cnt FROM sales")
sales_count = cursor.fetchone()['cnt']
print(f"   Всего: {sales_count}")

if sales_count > 0:
    cursor.execute("SELECT SUM(total_price) as total, SUM(for_pay) as to_pay FROM sales")
    s = cursor.fetchone()
    print(f"   💰 Сумма продаж: {s['total']:.2f} ₽")
    print(f"   💳 К выплате: {s['to_pay']:.2f} ₽")

# 4. Заказы
print("\n4. ЗАКАЗЫ (orders):")
cursor.execute("SELECT COUNT(*) as cnt FROM orders")
orders_count = cursor.fetchone()['cnt']
print(f"   Всего: {orders_count}")

cursor.execute("SELECT COUNT(*) as cnt FROM orders WHERE is_cancel = 1")
cancelled = cursor.fetchone()['cnt']
print(f"   Отменено: {cancelled}")
print(f"   Активных: {orders_count - cancelled}")

# 5. Проверка дат
print("\n5. ПЕРИОД ДАННЫХ:")
cursor.execute("SELECT MIN(rr_dt) as min_date, MAX(rr_dt) as max_date FROM financial_report")
dates = cursor.fetchone()
if dates['min_date']:
    min_date = dates['min_date'][:10]
    max_date = dates['max_date'][:10]
    print(f"   От: {min_date}")
    print(f"   До: {max_date}")

    # Вычисляем количество дней
    from datetime import datetime
    d1 = datetime.strptime(min_date, '%Y-%m-%d')
    d2 = datetime.strptime(max_date, '%Y-%m-%d')
    days_diff = (d2 - d1).days
    print(f"   Период: {days_diff} дней")

# 6. Данные за последний месяц
print("\n6. ЗА ПОСЛЕДНИЙ МЕСЯЦ:")
month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
cursor.execute("""
    SELECT
        SUM(retail_amount) as revenue,
        SUM(ppvz_for_pay) as to_pay,
        COUNT(*) as operations
    FROM financial_report
    WHERE DATE(rr_dt) >= ?
""", (month_ago,))
month_data = cursor.fetchone()
print(f"   Операций: {month_data['operations']}")
print(f"   Выручка: {month_data['revenue'] or 0:.2f} ₽")
print(f"   К выплате: {month_data['to_pay'] or 0:.2f} ₽")

conn.close()

print("\n" + "=" * 70)
print("✅ Проверка завершена! Если видишь реальные цифры - всё работает.")
print("=" * 70)
