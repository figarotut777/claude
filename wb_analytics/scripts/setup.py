#!/usr/bin/env python3
"""
Скрипт первичной настройки и инициализации системы
Выполняет полную синхронизацию данных за указанный период
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Добавление корневой директории в путь
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.services.data_sync import DataSyncService


def setup_logging():
    """Настройка логирования"""
    log_dir = ROOT_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / 'setup.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger(__name__)


def print_banner():
    """Вывод приветственного баннера"""
    print("\n" + "=" * 70)
    print("  Wildberries Analytics - Первичная настройка")
    print("=" * 70 + "\n")


def check_environment():
    """Проверка переменных окружения"""
    env_path = ROOT_DIR / '.env'

    if not env_path.exists():
        print("❌ Файл .env не найден!")
        print("\nСоздайте файл .env на основе .env.example:")
        print(f"  cp {ROOT_DIR}/.env.example {ROOT_DIR}/.env")
        print("\nЗатем отредактируйте .env и укажите ваш WB_API_KEY")
        sys.exit(1)

    load_dotenv(env_path)

    api_key = os.getenv('WB_API_KEY')

    if not api_key or api_key == 'your_wildberries_api_key_here':
        print("❌ WB_API_KEY не установлен!")
        print("\nОткройте файл .env и укажите ваш API ключ Wildberries")
        print("Получить API ключ можно в личном кабинете продавца WB:")
        print("  Настройки -> Доступ к API -> Создать новый токен")
        sys.exit(1)

    print("✓ Конфигурация загружена")
    return api_key


def main():
    """Главная функция"""
    print_banner()

    # Проверка окружения
    print("Проверка конфигурации...")
    api_key = check_environment()

    # Настройка логирования
    logger = setup_logging()

    logger.info("Начало первичной настройки системы")

    # Получение пути к БД
    db_path = os.getenv('DB_PATH', 'wb_analytics/data/wb_analytics.db')
    db_full_path = ROOT_DIR / db_path

    # Создание необходимых директорий
    print("\nСоздание структуры директорий...")
    (ROOT_DIR / 'data').mkdir(exist_ok=True)
    (ROOT_DIR / 'logs').mkdir(exist_ok=True)
    print("✓ Директории созданы")

    try:
        # Инициализация сервиса
        print("\nИнициализация сервиса синхронизации...")
        sync_service = DataSyncService(
            api_key=api_key,
            db_path=str(db_full_path)
        )
        print("✓ Сервис инициализирован")

        # Тест подключения
        print("\nТестирование подключения к Wildberries API...")
        if not sync_service.test_api_connection():
            print("❌ Не удалось подключиться к Wildberries API!")
            print("Проверьте корректность API ключа")
            sys.exit(1)

        print("✓ Подключение к API успешно")

        # Получение количества дней для загрузки
        days_back = int(os.getenv('INITIAL_SYNC_DAYS', 30))

        print(f"\n{'='*70}")
        print(f"Запуск полной синхронизации данных за последние {days_back} дней")
        print("Это может занять несколько минут...")
        print(f"{'='*70}\n")

        # Полная синхронизация
        stats = sync_service.sync_all_data(days_back=days_back)

        # Вывод результатов
        print("\n" + "=" * 70)
        print("✓ Первичная синхронизация завершена успешно!")
        print("-" * 70)
        print(f"Синхронизировано:")
        print(f"  - Продаж: {stats['sales']}")
        print(f"  - Заказов: {stats['orders']}")
        print(f"  - Остатков: {stats['stocks']}")
        print("=" * 70)

        # Получение статуса
        sync_status = sync_service.get_sync_status()
        print(f"\nВсего товаров в базе: {sync_status['total_products']}")
        print(f"Последняя синхронизация: {sync_status['last_full_sync']}")

        # Инструкции по дальнейшим действиям
        print("\n" + "=" * 70)
        print("Следующие шаги:")
        print("-" * 70)
        print("1. Настройте автоматическое обновление данных:")
        print(f"   bash {ROOT_DIR}/scripts/setup_cron.sh")
        print()
        print("2. Запустите веб-сервер для просмотра аналитики:")
        print(f"   python {ROOT_DIR}/scripts/start_server.py")
        print()
        print("3. Откройте в браузере: http://localhost:5000")
        print("=" * 70 + "\n")

        # Закрытие соединений
        sync_service.close()

        logger.info("Первичная настройка завершена успешно")
        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n❌ Настройка прервана пользователем")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Критическая ошибка при настройке: {e}", exc_info=True)
        print(f"\n❌ Ошибка: {e}")
        print("Подробности в логе: logs/setup.log")
        sys.exit(1)


if __name__ == '__main__':
    main()
