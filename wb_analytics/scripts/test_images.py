#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.database.models import generate_wb_image_url
import sqlite3

db_path = ROOT_DIR / 'data' / 'wb_analytics.db'
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("ПРОВЕРКА ГЕНЕРАЦИИ URL ИЗОБРАЖЕНИЙ")
print("=" * 80)

cursor.execute("SELECT nm_id, image_url FROM products LIMIT 5")

for row in cursor.fetchall():
    nm_id = row['nm_id']
    stored_url = row['image_url']
    generated_url = generate_wb_image_url(nm_id, size="tm")

    print(f"\nnm_id: {nm_id}")
    print(f"В БД:       {stored_url}")
    print(f"Генерация:  {generated_url}")
    print(f"Совпадает:  {'✓' if stored_url == generated_url else '✗'}")

conn.close()

print("\n" + "=" * 80)
print("Тестовая генерация URL для примера nm_id=228416131:")
test_nm_id = 228416131
for size in ['tm', 'c246x328', 'c516x688', 'big']:
    url = generate_wb_image_url(test_nm_id, size=size)
    print(f"  {size:12s}: {url}")
