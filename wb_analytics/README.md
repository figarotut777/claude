# 📊 Wildberries Analytics MVP

Собственный сервис аналитики для продавцов Wildberries с автоматическим сбором данных и интерактивным дашбордом.

## 🎯 Возможности

### Автоматический сбор данных
- ⏰ Обновление каждый час 24/7
- 📦 Продажи, заказы, остатки
- 🔄 Инкрементальная синхронизация
- 💾 История данных в SQLite

### Метрики и аналитика
- **Продажи**: количество, динамика, топ товаров
- **Выручка**: общая и по товарам
- **Прибыль**: после комиссии WB и с учётом себестоимости
- **ROI**: рентабельность продаж
- **Тренды**: процентное изменение vs предыдущий период
- **Остатки**: текущие запасы на складах

### Web Dashboard
- 📈 Интерактивные графики
- 🎨 Современный дизайн
- 📱 Адаптивная вёрстка
- ⚡ Реал-тайм обновления
- 🔍 Фильтры по периодам (сегодня, неделя, месяц, свой период)

## 📋 Требования

- Python 3.10 или выше
- Активный аккаунт продавца Wildberries
- API ключ Wildberries

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd wb_analytics
```

### 2. Установка зависимостей

```bash
# Создание виртуального окружения (рекомендуется)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt
```

### 3. Получение API ключа Wildberries

1. Войдите в [личный кабинет продавца WB](https://seller.wildberries.ru/)
2. Перейдите в **Настройки** → **Доступ к API**
3. Создайте новый токен со следующими правилами:
   - ✅ Статистика (Чтение)
   - ✅ Marketplace (Чтение)
4. Скопируйте сгенерированный API ключ

### 4. Настройка конфигурации

```bash
# Копирование примера конфигурации
cp .env.example .env

# Редактирование .env и установка API ключа
nano .env  # или любой другой редактор
```

В файле `.env` укажите ваш API ключ:

```env
WB_API_KEY=ваш_api_ключ_wildberries
```

### 5. Первичная инициализация

Запустите скрипт первичной настройки для загрузки истории данных:

```bash
python scripts/setup.py
```

Этот скрипт:
- ✅ Проверит подключение к WB API
- ✅ Создаст базу данных SQLite
- ✅ Загрузит данные за последние 30 дней
- ✅ Выведет статистику по товарам

### 6. Настройка автоматического обновления

Настройте cron для обновления данных каждый час:

```bash
chmod +x scripts/setup_cron.sh
bash scripts/setup_cron.sh
```

### 7. Запуск веб-сервера

```bash
python scripts/start_server.py
```

Откройте в браузере: **http://localhost:5000**

## 📁 Структура проекта

```
wb_analytics/
├── src/                          # Исходный код
│   ├── api/                      # API и веб-сервер
│   │   ├── wb_client.py         # Клиент Wildberries API
│   │   └── server.py            # Flask веб-сервер
│   ├── database/                 # Работа с БД
│   │   └── models.py            # SQLite модели
│   └── services/                 # Бизнес-логика
│       ├── data_sync.py         # Синхронизация данных
│       └── analytics.py         # Расчёт метрик
├── static/                       # Статические файлы
│   ├── css/                     # Стили
│   └── js/                      # JavaScript
├── templates/                    # HTML шаблоны
│   └── dashboard.html           # Дашборд
├── scripts/                      # Утилиты
│   ├── setup.py                 # Первичная настройка
│   ├── sync_data.py             # Синхронизация (для cron)
│   ├── start_server.py          # Запуск сервера
│   └── setup_cron.sh            # Настройка cron
├── data/                         # База данных (создаётся автоматически)
│   └── wb_analytics.db
├── logs/                         # Логи (создаётся автоматически)
├── .env.example                  # Пример конфигурации
├── requirements.txt              # Зависимости Python
└── README.md                     # Документация
```

## ⚙️ Конфигурация

### Переменные окружения (.env)

```env
# API ключ Wildberries (обязательно!)
WB_API_KEY=your_api_key_here

# Путь к базе данных
DB_PATH=wb_analytics/data/wb_analytics.db

# Порт веб-сервера
PORT=5000

# Режим отладки (True/False)
DEBUG=False

# Количество дней для первичной загрузки
INITIAL_SYNC_DAYS=30

# Хранение данных (дни)
DATA_RETENTION_DAYS=90

# Комиссия WB по умолчанию (%)
DEFAULT_WB_COMMISSION=15.0
```

### Настройка себестоимости и комиссии

Для точного расчёта прибыли установите себестоимость и комиссию WB для каждого товара через:

1. **Web Dashboard**: редактирование в таблице товаров
2. **API**: `PUT /api/products/{nm_id}/settings`
3. **Напрямую в БД**: таблица `products`, поля `cost_price` и `wb_commission_percent`

## 🔧 Управление

### Ручная синхронизация данных

```bash
python scripts/sync_data.py
```

### Запуск веб-сервера

```bash
python scripts/start_server.py
```

### Просмотр логов

```bash
# Логи синхронизации
tail -f logs/sync.log

# Логи cron
tail -f logs/cron.log

# Логи веб-сервера
tail -f logs/app.log
```

### Управление cron

```bash
# Просмотр текущих задач
crontab -l

# Редактирование задач
crontab -e

# Удаление задачи синхронизации
crontab -l | grep -v "sync_data.py" | crontab -
```

## 📊 API Endpoints

### Основные endpoints

- `GET /` - Web Dashboard
- `GET /api/health` - Статус API
- `GET /api/dashboard?period={today|week|month|custom}` - Данные дашборда
- `GET /api/metrics?period={period}&nm_id={id}` - Метрики
- `GET /api/products` - Список товаров
- `GET /api/products/{nm_id}` - Детали товара
- `PUT /api/products/{nm_id}/settings` - Обновление настроек товара
- `GET /api/top-products?period={period}&limit={n}` - Топ товаров
- `GET /api/stocks` - Остатки
- `GET /api/sync-status` - Статус синхронизации

### Примеры использования API

```bash
# Получение метрик за неделю
curl "http://localhost:5000/api/metrics?period=week"

# Топ-10 товаров за месяц
curl "http://localhost:5000/api/top-products?period=month&limit=10"

# Обновление себестоимости товара
curl -X PUT "http://localhost:5000/api/products/12345678/settings" \
  -H "Content-Type: application/json" \
  -d '{"cost_price": 500, "wb_commission": 15}'
```

## 🔐 Безопасность

### Защита API ключа

- ✅ Храните `.env` файл в `.gitignore`
- ✅ Никогда не коммитьте API ключ в Git
- ✅ Используйте переменные окружения
- ✅ Регулярно обновляйте API ключи

### Рекомендации

- Запускайте сервер за reverse proxy (nginx)
- Используйте HTTPS в продакшене
- Ограничьте доступ к серверу по IP
- Регулярно делайте бэкапы БД

## 🐛 Устранение неполадок

### Ошибка подключения к WB API

```
❌ Не удалось подключиться к Wildberries API!
```

**Решение:**
1. Проверьте корректность API ключа в `.env`
2. Убедитесь, что ключ имеет права на чтение статистики
3. Проверьте интернет-соединение

### База данных заблокирована

```
sqlite3.OperationalError: database is locked
```

**Решение:**
1. Остановите все процессы, использующие БД
2. Перезапустите сервер

### Cron не работает

**Проверка:**

```bash
# Проверьте, что задача добавлена
crontab -l

# Проверьте логи cron
grep CRON /var/log/syslog  # Ubuntu/Debian
tail -f logs/cron.log
```

## 📈 Масштабирование

### Для большого количества товаров (>100)

1. Увеличьте частоту синхронизации:
   ```bash
   # Каждые 30 минут вместо часа
   */30 * * * * cd /path/to/project && python scripts/sync_data.py
   ```

2. Настройте очистку старых данных:
   ```env
   DATA_RETENTION_DAYS=60  # Хранить 2 месяца вместо 3
   ```

3. Используйте PostgreSQL вместо SQLite для production

## 🤝 Поддержка

При возникновении проблем:

1. Проверьте логи в директории `logs/`
2. Убедитесь, что все зависимости установлены
3. Проверьте версию Python (≥3.10)

## 📝 Лицензия

MIT License - используйте свободно для коммерческих и некоммерческих целей.

## 🎓 Дополнительные ресурсы

- [Документация Wildberries API](https://openapi.wildberries.ru/)
- [Wildberries Seller Portal](https://seller.wildberries.ru/)

---

**Создано с ❤️ для продавцов Wildberries**
