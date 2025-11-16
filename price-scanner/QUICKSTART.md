# Price-Scanner - Quick Start Guide

## Быстрый старт за 5 минут

### 1. Предварительные требования

Убедитесь, что установлены:
- Docker 20.10+
- Docker Compose 2.0+

```bash
docker --version
docker-compose --version
```

### 2. Клонирование и настройка

```bash
# Клонировать репозиторий (если еще не клонирован)
git clone <repository-url>
cd price-scanner

# Создать .env файл
cp .env.example .env

# Отредактировать .env (опционально - для MVP работает с дефолтными значениями)
# nano .env
```

### 3. Запуск

```bash
# Запустить все сервисы
docker-compose up -d

# Дождаться запуска всех контейнеров (30-60 секунд)
docker-compose ps
```

### 4. Проверка

Откройте в браузере:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

### 5. Тестирование

**Text Search (через браузер):**
1. Откройте http://localhost:3000
2. Введите в поле поиска: "iPhone 15"
3. Нажмите "Search"

**API Test (через curl):**
```bash
curl -X POST http://localhost:8000/api/search/text \
  -H "Content-Type: application/json" \
  -d '{"query": "iPhone 15 Pro"}'
```

### 6. Остановка

```bash
# Остановить все сервисы
docker-compose down

# Остановить и удалить данные
docker-compose down -v
```

---

## Архитектура проекта

```
price-scanner/
├── backend/                    # Python Backend
│   ├── api/                   # API Gateway (FastAPI)
│   ├── services/              # Микросервисы
│   │   ├── image_search/     # Поиск по фото
│   │   ├── text_search/      # Поиск по тексту
│   │   ├── url_parser/       # Парсинг URL
│   │   ├── marketplace_connectors/  # Интеграции с маркетплейсами
│   │   └── normalizer/       # Нормализация данных
│   ├── models/               # SQLAlchemy модели
│   ├── database/             # SQL схемы
│   └── utils/                # Утилиты
├── frontend/                  # Next.js Frontend
│   ├── src/
│   │   ├── components/       # React компоненты
│   │   ├── pages/            # Next.js страницы
│   │   └── utils/            # API клиент
├── docker/                    # Dockerfiles
├── docs/                      # Документация
└── docker-compose.yml         # Оркестрация сервисов
```

---

## Доступные сервисы

| Сервис | URL | Описание |
|--------|-----|----------|
| Frontend | http://localhost:3000 | Веб-интерфейс |
| API Gateway | http://localhost:8000 | Основной API |
| API Docs | http://localhost:8000/docs | Swagger документация |
| Image Search | http://localhost:8001 | Поиск по фото |
| Text Search | http://localhost:8002 | Поиск по тексту |
| URL Parser | http://localhost:8003 | Парсинг URL |
| Marketplace | http://localhost:8004 | Интеграции |
| Normalizer | http://localhost:8005 | Нормализация |
| PostgreSQL | localhost:5432 | База данных |
| Redis | localhost:6379 | Кэш |

---

## Примеры использования

### 1. Поиск по тексту

```bash
curl -X POST http://localhost:8000/api/search/text \
  -H "Content-Type: application/json" \
  -d '{
    "query": "wireless headphones",
    "min_price": 50,
    "max_price": 200
  }'
```

### 2. Поиск по URL

```bash
curl -X POST http://localhost:8000/api/search/url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://amazon.com/product/..."
  }'
```

### 3. Список маркетплейсов

```bash
curl http://localhost:8004/marketplaces
```

---

## Настройка API ключей

Для полной функциональности добавьте API ключи в `.env`:

```env
# Google Vision API (для поиска по фото)
GOOGLE_VISION_API_KEY=your_key_here

# Marketplace APIs
AMAZON_API_KEY=your_key_here
EBAY_API_KEY=your_key_here
ALIEXPRESS_API_KEY=your_key_here
```

**Где получить ключи:**
- Google Vision: https://cloud.google.com/vision
- Amazon Product Advertising: https://affiliate-program.amazon.com
- eBay Developer: https://developer.ebay.com
- AliExpress Affiliate: https://portals.aliexpress.com

---

## Troubleshooting

### Проблема: Контейнер не запускается

```bash
# Проверить логи
docker-compose logs <service-name>

# Пересобрать образ
docker-compose build --no-cache <service-name>
docker-compose up -d
```

### Проблема: Порт уже занят

Измените порты в `docker-compose.yml`:
```yaml
services:
  frontend:
    ports:
      - "3001:3000"  # Вместо 3000:3000
```

### Проблема: База данных не инициализируется

```bash
# Удалить volume и пересоздать
docker-compose down -v
docker-compose up -d
```

---

## Следующие шаги

1. **Изучите документацию:**
   - API: [docs/API.md](docs/API.md)
   - Деплой: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

2. **Настройте маркетплейсы:**
   - Добавьте реальные API ключи
   - Настройте парсеры для конкретных сайтов

3. **Кастомизируйте frontend:**
   - Измените дизайн в `frontend/src/`
   - Добавьте новые компоненты

4. **Добавьте функционал:**
   - История цен
   - Watch-лист
   - Уведомления

---

## Поддержка

- GitHub Issues: https://github.com/yourusername/price-scanner/issues
- Email: support@price-scanner.com
- Документация: [docs/](docs/)

---

## Лицензия

MIT License - см. LICENSE файл
