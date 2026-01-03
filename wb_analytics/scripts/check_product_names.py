#!/usr/bin/env python3
import sys
import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
db_path = ROOT_DIR / 'data' / 'wb_analytics.db'

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("ПРОВЕРКА НАЗВАНИЙ ТОВАРОВ")
print("=" * 80)

# Проверим что в поле name
cursor.execute("""
    SELECT nm_id, name, subject, brand, article
    FROM products
    LIMIT 5
""")

print("\nПоля в таблице products:")
print(f"{'nm_id':<12} {'name':<30} {'subject':<20} {'brand':<15} {'article':<10}")
print("-" * 90)

for row in cursor.fetchall():
    name = (row['name'] or '')[:30]
    subject = (row['subject'] or '')[:20]
    brand = (row['brand'] or '')[:15]
    article = (row['article'] or '')[:10]
    print(f"{row['nm_id']:<12} {name:<30} {subject:<20} {brand:<15} {article:<10}")

# Проверим данные из financial_report (там тоже есть названия)
print("\n" + "=" * 80)
print("Названия из financial_report:")
print("-" * 80)

cursor.execute("""
    SELECT DISTINCT nm_id, subject_name, brand_name, sa_name
    FROM financial_report
    LIMIT 5
""")

for row in cursor.fetchall():
    print(f"nm_id: {row['nm_id']}")
    print(f"  subject_name: {row['subject_name']}")
    print(f"  brand_name: {row['brand_name']}")
    print(f"  sa_name (артикул): {row['sa_name']}")
    print()

conn.close()
