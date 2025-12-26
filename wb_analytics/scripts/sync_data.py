#!/usr/bin/env python3
"""
Скрипт синхронизации данных из Wildberries API
Предназначен для запуска по расписанию (cron)
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

    log_file = log_dir / 'sync.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger(__name__)


def main():
    """Главная функция"""
    # Загрузка переменных окружения
    env_path = ROOT_DIR / '.env'
    load_dotenv(env_path)

    # Настройка логирования
    logger = setup_logging()

    logger.info("=" * 70)
    logger.info("Начало синхронизации данных Wildberries")
    logger.info(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)

    # Получение API ключа
    api_key = os.getenv('WB_API_KEY')

    if not api_key or api_key == 'your_wildberries_api_key_here':
        logger.error("WB_API_KEY не установлен! Проверьте файл .env")
        logger.error("Скопируйте .env.example в .env и укажите ваш API ключ")
        sys.exit(1)

    # Получение пути к БД
    db_path = os.getenv('DB_PATH', 'wb_analytics/data/wb_analytics.db')
    db_full_path = ROOT_DIR / db_path

    # Создание директории для БД если не существует
    db_full_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Инициализация сервиса синхронизации
        logger.info(f"Инициализация сервиса с БД: {db_full_path}")
        sync_service = DataSyncService(
            api_key=api_key,
            db_path=str(db_full_path)
        )

        # Тест подключения к API
        logger.info("Проверка подключения к Wildberries API...")
        if not sync_service.test_api_connection():
            logger.error("Не удалось подключиться к Wildberries API!")
            logger.error("Проверьте корректность API ключа")
            sys.exit(1)

        logger.info("✓ Подключение к API успешно")

        # Инкрементальная синхронизация
        logger.info("Запуск инкрементальной синхронизации...")
        stats = sync_service.sync_incremental()

        # Вывод статистики
        logger.info("-" * 70)
        logger.info("Синхронизация завершена успешно!")
        logger.info(f"Синхронизировано:")
        logger.info(f"  - Продаж: {stats['sales']}")
        logger.info(f"  - Заказов: {stats['orders']}")
        logger.info(f"  - Остатков: {stats['stocks']}")
        logger.info("-" * 70)

        # Очистка старых данных (опционально, раз в день)
        current_hour = datetime.now().hour
        if current_hour == 3:  # В 3 часа ночи
            logger.info("Запуск очистки старых данных...")
            retention_days = int(os.getenv('DATA_RETENTION_DAYS', 90))
            sync_service.cleanup_old_data(days_to_keep=retention_days)

        # Закрытие соединений
        sync_service.close()

        logger.info("✓ Работа скрипта завершена успешно")
        sys.exit(0)

    except KeyboardInterrupt:
        logger.warning("Синхронизация прервана пользователем")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Критическая ошибка при синхронизации: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
