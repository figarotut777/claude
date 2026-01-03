#!/usr/bin/env python3
"""
Детальная проверка финансовых данных
"""
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.models import DatabaseManager

db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'wb_analytics.db')
db = DatabaseManager(db_path)

print("=" * 70)
print("Детальная проверка финансовых данных")
print("=" * 70)

with db.get_connection() as conn:
    cursor = conn.cursor()

    # Проверка структуры таблицы
    cursor.execute("PRAGMA table_info(financial_report)")
    columns = cursor.fetchall()
    print("\n📋 Структура таблицы financial_report:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")

    # Получение одной полной записи для анализа
    cursor.execute("SELECT * FROM financial_report LIMIT 1")
    row = cursor.fetchone()

    if row:
        print("\n📊 Пример записи (первая строка):")
        for i, col in enumerate(columns):
            col_name = col[1]
            value = row[i] if i < len(row) else None
            print(f"  {col_name}: {value}")

    # Статистика по типам операций
    cursor.execute("""
        SELECT doc_type_name, COUNT(*) as count,
               SUM(retail_amount) as total_revenue,
               SUM(ppvz_for_pay) as total_to_pay
        FROM financial_report
        GROUP BY doc_type_name
    """)

    print("\n📈 Статистика по типам операций:")
    types = cursor.fetchall()
    for t in types:
        print(f"  {t[0] or 'NULL'}: {t[1]} записей, выручка: {t[2] or 0} ₽, к выплате: {t[3] or 0} ₽")

    # Проверка записей с ненулевыми суммами
    cursor.execute("""
        SELECT COUNT(*)
        FROM financial_report
        WHERE retail_amount > 0 OR ppvz_for_pay > 0
    """)
    non_zero = cursor.fetchone()[0]
    print(f"\n💰 Записей с ненулевыми суммами: {non_zero}")

    if non_zero > 0:
        cursor.execute("""
            SELECT sale_dt, sa_name, doc_type_name, retail_amount, ppvz_for_pay
            FROM financial_report
            WHERE retail_amount > 0 OR ppvz_for_pay > 0
            ORDER BY sale_dt DESC
            LIMIT 5
        """)
        print("\nПримеры ненулевых записей:")
        for r in cursor.fetchall():
            print(f"  {r[0]} | {r[1]} | {r[2]} | {r[3]} ₽ | {r[4]} ₽")

print("\n" + "=" * 70)
