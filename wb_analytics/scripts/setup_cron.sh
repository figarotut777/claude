#!/bin/bash
# Скрипт настройки cron для автоматического обновления данных каждый час

set -e

echo "=================================================="
echo "  Настройка автоматического обновления данных"
echo "=================================================="
echo

# Определение директории проекта
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Путь к Python скрипту синхронизации
SYNC_SCRIPT="$PROJECT_DIR/scripts/sync_data.py"

# Путь к Python интерпретатору
PYTHON_BIN=$(which python3)

if [ -z "$PYTHON_BIN" ]; then
    echo "❌ Python 3 не найден!"
    exit 1
fi

echo "Путь к проекту: $PROJECT_DIR"
echo "Python: $PYTHON_BIN"
echo "Скрипт синхронизации: $SYNC_SCRIPT"
echo

# Проверка существования скрипта
if [ ! -f "$SYNC_SCRIPT" ]; then
    echo "❌ Скрипт синхронизации не найден: $SYNC_SCRIPT"
    exit 1
fi

# Создание задачи cron (запуск каждый час)
CRON_JOB="0 * * * * cd $PROJECT_DIR && $PYTHON_BIN $SYNC_SCRIPT >> $PROJECT_DIR/logs/cron.log 2>&1"

echo "Задача cron для добавления:"
echo "$CRON_JOB"
echo

# Проверка, не добавлена ли уже эта задача
if crontab -l 2>/dev/null | grep -q "$SYNC_SCRIPT"; then
    echo "⚠️  Задача cron уже существует!"
    echo
    read -p "Хотите обновить задачу? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Отменено."
        exit 0
    fi

    # Удаление старой задачи
    (crontab -l 2>/dev/null | grep -v "$SYNC_SCRIPT") | crontab -
fi

# Добавление новой задачи
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✓ Задача cron успешно добавлена!"
echo
echo "Данные будут обновляться автоматически каждый час."
echo "Логи сохраняются в: $PROJECT_DIR/logs/cron.log"
echo
echo "Для просмотра текущих задач cron выполните:"
echo "  crontab -l"
echo
echo "Для удаления задачи выполните:"
echo "  crontab -e"
echo "  # и удалите строку с wb_analytics"
echo

exit 0
