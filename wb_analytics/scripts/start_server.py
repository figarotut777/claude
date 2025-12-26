#!/usr/bin/env python3
"""
Скрипт запуска веб-сервера для dashboard
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Добавление корневой директории в путь
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Загрузка переменных окружения
env_path = ROOT_DIR / '.env'
load_dotenv(env_path)

# Изменение рабочей директории
os.chdir(ROOT_DIR)

# Импорт и запуск Flask приложения
from src.api.server import app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'

    print("\n" + "=" * 70)
    print("  Wildberries Analytics - Web Dashboard")
    print("=" * 70)
    print(f"\nСервер запущен на: http://localhost:{port}")
    print("Нажмите Ctrl+C для остановки\n")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
