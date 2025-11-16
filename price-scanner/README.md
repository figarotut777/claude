# Price-Scanner MVP

Единый интерфейс для поиска и сравнения цен по фото, названию и URL на нескольких маркетплейсах одновременно.

## Возможности

- **Поиск по фото**: Загрузка изображения и поиск похожих товаров через Vision API
- **Поиск по названию**: Текстовый поиск с нечетким совпадением (fuzzy search)
- **Поиск по URL**: Парсинг товара по ссылке и поиск аналогов
- **Сравнение цен**: Единый интерфейс сравнения на нескольких маркетплейсах
- **Кэширование**: Redis для быстрых повторных запросов
- **Масштабируемость**: Микросервисная архитектура на Docker

## Архитектура

```
┌─────────────┐
│   Frontend  │  (Next.js + React)
│  (Port 3000)│
└──────┬──────┘
       │
┌──────▼──────┐
│   API       │  (FastAPI)
│ Gateway     │  (Port 8000)
└──────┬──────┘
       │
       ├────► Image Search Service (Port 8001)
       ├────► Text Search Service (Port 8002)
       ├────► URL Parser Service (Port 8003)
       ├────► Marketplace Connectors (Port 8004)
       └────► Product Normalizer (Port 8005)

┌──────────────────────────────┐
│  Infrastructure              │
├──────────────┬───────────────┤
│ PostgreSQL   │ Redis Cache   │
│ (Port 5432)  │ (Port 6379)   │
└──────────────┴───────────────┘
```

## Быстрый старт

### Требования

- Docker & Docker Compose
- Node.js 18+ (для локальной разработки frontend)
- Python 3.11+ (для локальной разработки backend)

### Запуск всех сервисов

```bash
# Клонировать репозиторий
git clone <repo-url>
cd price-scanner

# Запустить все сервисы через Docker Compose
docker-compose up -d

# Проверить статус
docker-compose ps

# Логи
docker-compose logs -f
```

Сервисы будут доступны:
- Frontend: http://localhost:3000
- API Gateway: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Локальная разработка

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Запустить API Gateway
uvicorn api.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Структура проекта

```
price-scanner/
├── backend/
│   ├── services/
│   │   ├── image_search/       # Vision API поиск по фото
│   │   ├── text_search/        # Fuzzy text поиск
│   │   ├── url_parser/         # Парсинг товаров по URL
│   │   ├── marketplace_connectors/  # Интеграции с маркетплейсами
│   │   └── normalizer/         # Нормализация данных товаров
│   ├── api/                    # API Gateway
│   ├── models/                 # Модели данных (SQLAlchemy)
│   ├── database/               # Миграции и схемы БД
│   └── utils/                  # Утилиты
├── frontend/
│   ├── src/
│   │   ├── components/         # React компоненты
│   │   ├── pages/              # Next.js страницы
│   │   ├── utils/              # Утилиты
│   │   └── styles/             # CSS/SCSS
├── docker/                     # Dockerfile'ы для сервисов
├── docs/                       # Документация
└── .github/workflows/          # CI/CD
```

## API Endpoints

### Поиск

- `POST /api/search/image` - Поиск по фото
- `POST /api/search/text` - Поиск по названию
- `POST /api/search/url` - Поиск по URL товара

### Товары

- `GET /api/products/{id}` - Получить товар
- `GET /api/products/compare` - Сравнить товары

### История

- `GET /api/history` - История поисков
- `DELETE /api/history/{id}` - Удалить из истории

## Маркетплейсы (MVP)

Текущие интеграции:
- Amazon (API + Parser)
- eBay (API)
- AliExpress (Parser)
- Wildberries (Parser)
- Ozon (Parser)

## Технологии

**Backend:**
- Python 3.11
- FastAPI
- PostgreSQL 15
- Redis 7
- SQLAlchemy
- Celery (для фоновых задач)
- BeautifulSoup4 / Selenium (парсинг)

**Frontend:**
- Next.js 14
- React 18
- TypeScript
- TailwindCSS
- SWR (data fetching)

**Infrastructure:**
- Docker & Docker Compose
- Nginx (reverse proxy)
- Prometheus + Grafana (мониторинг)

## Конфигурация

Создайте `.env` файл в корне проекта:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/price_scanner
REDIS_URL=redis://localhost:6379

# API Keys
GOOGLE_VISION_API_KEY=your_key_here
AMAZON_API_KEY=your_key_here
EBAY_API_KEY=your_key_here
ALIEXPRESS_API_KEY=your_key_here

# Settings
DEBUG=true
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

## Тестирование

```bash
# Backend тесты
cd backend
pytest

# Frontend тесты
cd frontend
npm test

# E2E тесты
npm run test:e2e
```

## Деплой

```bash
# Production build
docker-compose -f docker-compose.prod.yml up -d

# Миграции БД
docker-compose exec api alembic upgrade head
```

## Roadmap

### MVP (текущая версия)
- [x] Архитектура проекта
- [x] Базовый поиск (фото, текст, URL)
- [x] Интеграция с основными маркетплейсами
- [x] Веб-интерфейс
- [x] Кэширование

### v1.1
- [ ] История цен (price tracking)
- [ ] Уведомления о снижении цен
- [ ] Watch-лист товаров
- [ ] Браузерное расширение

### v2.0
- [ ] Мобильное приложение
- [ ] Расширенная аналитика
- [ ] API для бизнеса
- [ ] ML-рекомендации

## Монетизация

1. **Free tier**: 10 запросов/день
2. **Pro ($9.99/мес)**: Безлимит + история + экспорт
3. **Enterprise**: Custom API + поддержка

## Лицензия

MIT License

## Контакты

- Issues: GitHub Issues
- Email: support@price-scanner.com
