# 🎱 Billiards Booking App

Современное кросс-платформенное приложение для бронирования столов в бильярдном клубе с визуальным таймлайном и поддержкой "переходящих" суток (работа с 12:00 до 04:00 следующего дня).

## 📋 Содержание

- [Возможности](#возможности)
- [Технологический стек](#технологический-стек)
- [Быстрый старт](#быстрый-старт)
- [Архитектура](#архитектура)
- [Структура проекта](#структура-проекта)
- [API документация](#api-документация)
- [Разработка](#разработка)

---

## ✨ Возможности

### Для клиентов:
- 📊 **Визуальный таймлайн** - наглядное отображение занятости столов по времени
- 📅 **Простое бронирование** - интуитивный интерфейс создания бронирований
- 🎯 **Типы столов** - разделение на Русский бильярд и Американский пул
- 🕐 **Переходящие сутки** - корректная работа с графиком 12:00-04:00
- 📱 **Кросс-платформа** - iOS и Android из одной кодовой базы
- 🔄 **Live-обновления** - автоматическое обновление через WebSocket

### Для администраторов:
- ⚙️ **Управление столами** - гибкая настройка количества столов каждого типа
- 📈 **Аналитика** - просмотр всех бронирований
- 🎨 **Настройка типов** - кастомизация цветов и названий

---

## 🛠 Технологический стек

### Backend
- **Node.js** - серверная платформа
- **Express** - веб-фреймворк
- **Prisma ORM** - типобезопасная работа с БД
- **PostgreSQL** - реляционная база данных
- **Socket.io** - WebSocket для real-time обновлений
- **Docker** - контейнеризация

### Mobile App
- **React Native** - кросс-платформенная разработка
- **Expo** - инструментарий и SDK
- **Expo Router** - файловая навигация
- **React Query** - управление серверным состоянием
- **Zustand** - клиентское state management
- **date-fns** - работа с датами

---

## 🚀 Быстрый старт

### Предварительные требования

- **Node.js** 18+ и npm
- **Docker** и Docker Compose (для запуска через контейнеры)
- **Expo CLI** (для mobile разработки)

### Вариант 1: Запуск с Docker (рекомендуется)

```bash
# 1. Клонировать репозиторий
cd billiards-booking

# 2. Запустить backend и базу данных
docker-compose up -d

# 3. Применить миграции и seed данных
docker-compose exec backend npx prisma db push
docker-compose exec backend npm run db:seed

# Backend запущен на http://localhost:3000
```

### Вариант 2: Локальный запуск

#### Backend

```bash
cd billiards-booking/backend

# Установить зависимости
npm install

# Настроить .env файл
cp .env.example .env
# Отредактируйте .env и укажите DATABASE_URL

# Запустить PostgreSQL локально или через Docker:
docker run --name billiards-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=billiards \
  -p 5432:5432 \
  -d postgres:16-alpine

# Применить схему БД
npx prisma db push

# Заполнить начальными данными
npm run db:seed

# Запустить в dev режиме
npm run dev
```

Backend будет доступен на `http://localhost:3000`

#### Mobile App

```bash
cd billiards-booking/mobile

# Установить зависимости
npm install

# Запустить Expo development server
npx expo start

# Сканируйте QR код в Expo Go app или:
# - Нажмите 'i' для iOS simulator
# - Нажмите 'a' для Android emulator
# - Нажмите 'w' для web версии
```

**Важно!** Убедитесь, что в `mobile/src/config/api.js` указан правильный URL backend'а:
- Для физического устройства: используйте IP адрес компьютера (например, `http://192.168.1.100:3000/api`)
- Для эмулятора Android: `http://10.0.2.2:3000/api`
- Для симулятора iOS: `http://localhost:3000/api`

---

## 🏗 Архитектура

### Концепция "Business Date" (Переходящие сутки)

Клуб работает с **12:00 (полдень)** до **04:00 (утра следующего дня)**.

**Ключевая логика:**
- Если текущее время 00:00-03:59, то **business date = предыдущий день**
- Пример: 02:00 AM 16 ноября → business date = 15 ноября
- Это обеспечивает логичную группировку бронирований по "рабочим дням"

```javascript
// Пример из кода
function getBusinessDate(datetime = new Date()) {
  const hour = datetime.getHours();

  if (hour >= 0 && hour < 4) {
    const businessDate = new Date(datetime);
    businessDate.setDate(businessDate.getDate() - 1);
    return startOfDay(businessDate);
  }

  return startOfDay(datetime);
}
```

### Визуальный таймлайн

**Ось X:** Время (12:00, 13:00, ..., 23:00, 00:00, 01:00, 02:00, 03:00, 04:00)
**Ось Y:** Столы, сгруппированные по типам

```
┌─────────────────────────────────────────────────────────┐
│  12:00   14:00   16:00   18:00   20:00   22:00   02:00 │
├─────────────────────────────────────────────────────────┤
│ Русский бильярд                                         │
│ Стол #1  │█████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│  │
│ Стол #2  │░░░░░░░░░░░░█████████████░░░░░░░░░░░░░░░░│  │
│                                                         │
│ Американский пул                                        │
│ Стол #1  │░░░░░░░░░░░░░░░░░░░░░█████████░░░░░░░░░░░│  │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Структура проекта

```
billiards-booking/
├── backend/                    # Node.js Backend
│   ├── prisma/
│   │   └── schema.prisma      # Database schema
│   ├── src/
│   │   ├── routes/            # API endpoints
│   │   │   ├── bookings.js    # Booking routes
│   │   │   ├── tables.js      # Table routes
│   │   │   ├── tableTypes.js  # Table type routes
│   │   │   └── settings.js    # Settings routes
│   │   ├── utils/
│   │   │   └── businessDate.js # Business date logic
│   │   ├── seed.js            # Database seeding
│   │   └── index.js           # Server entry point
│   ├── .env                   # Environment variables
│   ├── package.json
│   └── Dockerfile
│
├── mobile/                     # React Native App
│   ├── app/                   # Expo Router pages
│   │   ├── _layout.js         # Root layout
│   │   ├── index.js           # Home (Timeline view)
│   │   ├── booking/
│   │   │   ├── create.js      # Create booking
│   │   │   └── [id].js        # Booking details
│   │   └── admin/
│   │       └── index.js       # Admin panel
│   ├── src/
│   │   ├── components/
│   │   │   └── Timeline/
│   │   │       └── TimelineView.js  # Main timeline component
│   │   ├── config/
│   │   │   └── api.js         # API configuration
│   │   ├── services/          # API services
│   │   ├── theme/             # Design system
│   │   └── utils/             # Utilities
│   ├── app.json               # Expo config
│   └── package.json
│
├── docker-compose.yml         # Docker orchestration
└── README.md                  # This file
```

---

## 📡 API документация

### Base URL
```
http://localhost:3000/api
```

### Endpoints

#### Table Types

```bash
# Get all table types
GET /api/table-types

# Response:
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "russian",
      "displayName": "Русский бильярд",
      "sortOrder": 1,
      "color": "#8B5CF6",
      "_count": { "tables": 5 }
    }
  ]
}
```

#### Tables

```bash
# Get all tables
GET /api/tables?typeId=1&includeInactive=false

# Create table
POST /api/tables
{
  "typeId": 1,
  "number": 6
}

# Bulk update table count
POST /api/tables/bulk-update-count
{
  "typeId": 1,
  "count": 10
}
```

#### Bookings

```bash
# Get timeline for a date
GET /api/bookings/timeline?businessDate=2024-11-16

# Response:
{
  "success": true,
  "data": {
    "businessDate": "2024-11-16",
    "tableTypes": [
      {
        "id": 1,
        "displayName": "Русский бильярд",
        "tables": [
          {
            "id": 1,
            "number": 1,
            "bookings": [
              {
                "id": 1,
                "startDatetime": "2024-11-16T14:00:00Z",
                "endDatetime": "2024-11-16T16:00:00Z",
                "customerName": "Иван Петров",
                "status": "ACTIVE"
              }
            ]
          }
        ]
      }
    ]
  }
}

# Create booking
POST /api/bookings
{
  "tableId": 1,
  "startDatetime": "2024-11-16T14:00:00Z",
  "endDatetime": "2024-11-16T16:00:00Z",
  "customerName": "Иван Петров",
  "customerPhone": "+7 (999) 123-45-67"
}

# Cancel booking
DELETE /api/bookings/1
```

### WebSocket Events

```javascript
// Connect to WebSocket
const socket = io('http://localhost:3000');

// Join a specific business date room
socket.emit('join-date', '2024-11-16');

// Listen for booking events
socket.on('booking-created', (booking) => {
  console.log('New booking:', booking);
});

socket.on('booking-updated', (booking) => {
  console.log('Updated booking:', booking);
});

socket.on('booking-cancelled', (booking) => {
  console.log('Cancelled booking:', booking);
});
```

---

## 👨‍💻 Разработка

### Backend

```bash
cd backend

# Run development server with auto-reload
npm run dev

# View database in Prisma Studio
npm run db:studio

# Reset database and reseed
npx prisma db push --force-reset
npm run db:seed
```

### Mobile

```bash
cd mobile

# Start development server
npx expo start

# Clear cache and restart
npx expo start -c

# Run on specific platform
npx expo start --ios
npx expo start --android
```

### Полезные команды

```bash
# Просмотр логов Docker
docker-compose logs -f backend

# Остановить все контейнеры
docker-compose down

# Пересобрать контейнеры
docker-compose up --build

# Подключиться к PostgreSQL
docker-compose exec postgres psql -U postgres -d billiards
```

---

## 🎨 Кастомизация

### Изменение цветов типов столов

В `mobile/src/theme/colors.js`:

```javascript
tableTypes: {
  russian: '#8B5CF6',      // Фиолетовый
  americanPool: '#F59E0B', // Оранжевый
}
```

### Изменение часов работы

В `backend/.env`:

```env
CLUB_OPENING_HOUR=12
CLUB_CLOSING_HOUR=4
```

---

## 📝 Начальные данные (seed)

После запуска `npm run db:seed` создаются:

- **2 типа столов**: Русский бильярд, Американский пул
- **15 столов**: 5 русских + 10 американских
- **2 примера бронирований** на сегодня

---

## 🔐 Безопасность

- ✅ Валидация всех входных данных
- ✅ Проверка перекрытия бронирований
- ✅ Проверка времени работы клуба
- ✅ CORS настроен (настройте для production!)
- ⚠️ **TODO**: Добавить аутентификацию для admin панели

---

## 🚢 Деплой

### Backend на Railway/Render

1. Создайте PostgreSQL базу данных
2. Установите переменную окружения `DATABASE_URL`
3. Деплой через Git или Docker

### Mobile на App Store / Google Play

```bash
# Build для iOS
eas build --platform ios

# Build для Android
eas build --platform android
```

---

## 📄 Лицензия

MIT License - свободное использование для коммерческих и некоммерческих проектов.

---

## 🤝 Поддержка

Если у вас возникли вопросы или проблемы:

1. Проверьте что backend запущен (`http://localhost:3000/health`)
2. Проверьте DATABASE_URL в `.env`
3. Убедитесь что mobile приложение указывает на правильный API URL
4. Очистите кеш: `npx expo start -c`

---

**Разработано с ❤️ для бильярдных клубов**
