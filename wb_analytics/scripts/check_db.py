#!/usr/bin/env python3
"""
Проверка содержимого базы данных
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.models import DatabaseManager

db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'wb_analytics.db')
db = DatabaseManager(db_path)

print("=" * 70)
print("Содержимое базы данных WB Analytics")
print("=" * 70)

with db.get_connection() as conn:
    cursor = conn.cursor()

    # Товары
    cursor.execute("SELECT COUNT(*) FROM products")
    products_count = cursor.fetchone()[0]
    print(f"\n📦 Товаров: {products_count}")

    if products_count > 0:
        cursor.execute("SELECT nm_id, article, name FROM products LIMIT 5")
        products = cursor.fetchall()
        print("\nПримеры товаров:")
        for p in products:
            print(f"  - {p[0]} | {p[1]} | {p[2]}")

    # Продажи
    cursor.execute("SELECT COUNT(*) FROM sales")
    sales_count = cursor.fetchone()[0]
    print(f"\n💰 Продаж: {sales_count}")

    if sales_count > 0:
        cursor.execute("SELECT date, nm_id, total_price FROM sales ORDER BY date DESC LIMIT 5")
        sales = cursor.fetchall()
        print("\nПоследние продажи:")
        for s in sales:
            print(f"  - {s[0]} | NM {s[1]} | {s[2]} ₽")

    # Финансовый отчёт
    cursor.execute("SELECT COUNT(*) FROM financial_report")
    financial_count = cursor.fetchone()[0]
    print(f"\n📊 Финансовых записей: {financial_count}")

    if financial_count > 0:
        cursor.execute("""
            SELECT sale_dt, sa_name, retail_amount, ppvz_for_pay
            FROM financial_report
            ORDER BY sale_dt DESC
            LIMIT 5
        """)
        financial = cursor.fetchall()
        print("\nПоследние финансовые записи:")
        for f in financial:
            print(f"  - {f[0]} | {f[1]} | Выручка: {f[2]} ₽ | К выплате: {f[3]} ₽")

    # Остатки
    cursor.execute("SELECT COUNT(*) FROM stocks")
    stocks_count = cursor.fetchone()[0]
    print(f"\n📦 Остатков: {stocks_count}")

    # Проверка на тестовые данные
    cursor.execute("SELECT COUNT(*) FROM products WHERE article LIKE 'ART-%'")
    test_products = cursor.fetchone()[0]

    print("\n" + "=" * 70)
    if test_products > 0:
        print(f"⚠️  ОБНАРУЖЕНЫ ТЕСТОВЫЕ ДАННЫЕ! ({test_products} товаров с артикулами ART-*)")
        print("   Это НЕ реальные данные из Wildberries API!")
    else:
        print("✓ Тестовых данных не обнаружено")
    print("=" * 70)
