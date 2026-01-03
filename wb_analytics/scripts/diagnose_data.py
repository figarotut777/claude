#!/usr/bin/env python3
"""
Диагностика данных в базе - проверяем все таблицы
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

# Добавление корневой директории в путь
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
print("ДИАГНОСТИКА БАЗЫ ДАННЫХ")
print("=" * 70)

# 1. Товары
print("\n1. ТОВАРЫ (products):")
cursor.execute("SELECT COUNT(*) as cnt FROM products")
print(f"   Всего товаров: {cursor.fetchone()['cnt']}")

cursor.execute("SELECT nm_id, subject, brand FROM products LIMIT 5")
products = cursor.fetchall()
for p in products:
    print(f"   - {p['nm_id']}: {p['brand']} - {p['subject']}")

# 2. Продажи
print("\n2. ПРОДАЖИ (sales):")
cursor.execute("SELECT COUNT(*) as cnt FROM sales")
total_sales = cursor.fetchone()['cnt']
print(f"   Всего записей: {total_sales}")

if total_sales > 0:
    cursor.execute("""
        SELECT date, nm_id, total_price, for_pay
        FROM sales
        ORDER BY date DESC
        LIMIT 5
    """)
    sales = cursor.fetchall()
    print("   Последние 5 продаж:")
    for s in sales:
        print(f"   - {s['date']}: nm_id={s['nm_id']}, price={s['total_price']}, to_pay={s['for_pay']}")

    # Статистика по датам
    cursor.execute("""
        SELECT
            DATE(date) as sale_date,
            COUNT(*) as cnt,
            SUM(total_price) as revenue
        FROM sales
        GROUP BY sale_date
        ORDER BY sale_date DESC
        LIMIT 10
    """)
    print("\n   Продажи по дням:")
    for row in cursor.fetchall():
        print(f"   - {row['sale_date']}: {row['cnt']} продаж, {row['revenue']} руб")

# 3. Заказы
print("\n3. ЗАКАЗЫ (orders):")
cursor.execute("SELECT COUNT(*) as cnt FROM orders")
total_orders = cursor.fetchone()['cnt']
print(f"   Всего записей: {total_orders}")

if total_orders > 0:
    cursor.execute("""
        SELECT date, nm_id, total_price, is_cancel
        FROM orders
        ORDER BY date DESC
        LIMIT 5
    """)
    orders = cursor.fetchall()
    print("   Последние 5 заказов:")
    for o in orders:
        cancel_status = "(отменён)" if o['is_cancel'] else ""
        print(f"   - {o['date']}: nm_id={o['nm_id']}, price={o['total_price']} {cancel_status}")

# 4. Финансовый отчёт
print("\n4. ФИНАНСОВЫЙ ОТЧЁТ (financial_report):")
cursor.execute("SELECT COUNT(*) as cnt FROM financial_report")
total_financial = cursor.fetchone()['cnt']
print(f"   Всего записей: {total_financial}")

if total_financial > 0:
    # Первые записи
    cursor.execute("""
        SELECT
            rr_dt,
            nm_id,
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
    print("\n   Первые 10 записей:")
    for row in cursor.fetchall():
        print(f"   - {row['rr_dt']}: nm_id={row['nm_id']}")
        print(f"     doc_type={row['doc_type_name']}, oper={row['supplier_oper_name']}")
        print(f"     qty={row['quantity']}, retail={row['retail_amount']}, to_pay={row['ppvz_for_pay']}")
        print(f"     storage={row['storage_fee']}, penalty={row['penalty']}")

    # Суммарная статистика
    cursor.execute("""
        SELECT
            COUNT(*) as cnt,
            SUM(retail_amount) as total_retail,
            SUM(ppvz_for_pay) as total_to_pay,
            SUM(storage_fee) as total_storage,
            SUM(penalty) as total_penalty,
            SUM(delivery_rub) as total_delivery
        FROM financial_report
    """)
    stats = cursor.fetchone()
    print(f"\n   СУММАРНАЯ СТАТИСТИКА:")
    print(f"   - Записей: {stats['cnt']}")
    print(f"   - Выручка: {stats['total_retail']} руб")
    print(f"   - К выплате: {stats['total_to_pay']} руб")
    print(f"   - Хранение: {stats['total_storage']} руб")
    print(f"   - Штрафы: {stats['total_penalty']} руб")
    print(f"   - Логистика: {stats['total_delivery']} руб")

    # По типам документов
    cursor.execute("""
        SELECT
            doc_type_name,
            COUNT(*) as cnt,
            SUM(retail_amount) as total_retail,
            SUM(ppvz_for_pay) as total_to_pay
        FROM financial_report
        GROUP BY doc_type_name
        ORDER BY cnt DESC
    """)
    print(f"\n   ПО ТИПАМ ДОКУМЕНТОВ:")
    for row in cursor.fetchall():
        doc_type = row['doc_type_name'] or '(пусто)'
        print(f"   - {doc_type}: {row['cnt']} записей, retail={row['total_retail']}, to_pay={row['total_to_pay']}")

# 5. Проверка дат
print("\n5. ПРОВЕРКА ДАТ:")
now = datetime.now()
today = now.date()
week_ago = today - timedelta(days=7)
month_ago = today - timedelta(days=30)

print(f"   Сегодня: {today}")
print(f"   Неделю назад: {week_ago}")
print(f"   Месяц назад: {month_ago}")

# Продажи за сегодня
cursor.execute("SELECT COUNT(*) as cnt FROM sales WHERE DATE(date) = ?", (str(today),))
print(f"   Продажи сегодня: {cursor.fetchone()['cnt']}")

# Продажи за неделю
cursor.execute("SELECT COUNT(*) as cnt FROM sales WHERE DATE(date) >= ?", (str(week_ago),))
print(f"   Продажи за неделю: {cursor.fetchone()['cnt']}")

# Продажи за месяц
cursor.execute("SELECT COUNT(*) as cnt FROM sales WHERE DATE(date) >= ?", (str(month_ago),))
print(f"   Продажи за месяц: {cursor.fetchone()['cnt']}")

# Финансовый отчёт за сегодня
cursor.execute("SELECT COUNT(*) as cnt FROM financial_report WHERE DATE(rr_dt) = ?", (str(today),))
print(f"   Финансовый отчёт сегодня: {cursor.fetchone()['cnt']}")

# Финансовый отчёт за неделю
cursor.execute("SELECT COUNT(*) as cnt FROM financial_report WHERE DATE(rr_dt) >= ?", (str(week_ago),))
print(f"   Финансовый отчёт за неделю: {cursor.fetchone()['cnt']}")

# Финансовый отчёт за месяц
cursor.execute("SELECT COUNT(*) as cnt FROM financial_report WHERE DATE(rr_dt) >= ?", (str(month_ago),))
print(f"   Финансовый отчёт за месяц: {cursor.fetchone()['cnt']}")

conn.close()

print("\n" + "=" * 70)
print("ДИАГНОСТИКА ЗАВЕРШЕНА")
print("=" * 70)
