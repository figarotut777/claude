#!/usr/bin/env python3
"""
Проверка структуры таблиц в базе данных
"""

import sys
import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

db_path = ROOT_DIR / 'data' / 'wb_analytics.db'

if not db_path.exists():
    print(f"❌ База данных не найдена: {db_path}")
    sys.exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Получаем список всех таблиц
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("=" * 70)
print("СТРУКТУРА БАЗЫ ДАННЫХ")
print("=" * 70)

for table in tables:
    table_name = table[0]
    print(f"\n📋 Таблица: {table_name}")
    print("-" * 70)

    # Получаем информацию о колонках
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()

    for col in columns:
        col_id, col_name, col_type, not_null, default_val, pk = col
        pk_mark = " [PK]" if pk else ""
        not_null_mark = " NOT NULL" if not_null else ""
        default_mark = f" DEFAULT {default_val}" if default_val else ""
        print(f"  {col_name:30s} {col_type:15s}{pk_mark}{not_null_mark}{default_mark}")

    # Показываем количество записей
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"\n  📊 Записей: {count}")

conn.close()

print("\n" + "=" * 70)
