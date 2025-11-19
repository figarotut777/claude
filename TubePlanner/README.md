# TubePlanner — YouTube Action Plan Generator

> Превращайте обучающие видео с YouTube в четкие пошаговые чек-листы

![macOS](https://img.shields.io/badge/macOS-14.0+-blue)
![Swift](https://img.shields.io/badge/Swift-5.9+-orange)
![SwiftUI](https://img.shields.io/badge/SwiftUI-Native-green)

## 🎯 Что это?

**TubePlanner** — нативное macOS-приложение, которое автоматически генерирует пошаговые планы действий (Action Plans) из обучающих видео YouTube.

### Проблема
- Смотреть 40-минутный туториал долго
- Записывать шаги вручную — лень
- Легко потерять конспекты

### Решение
1. Вставьте ссылку на YouTube
2. Приложение получает транскрипт
3. ИИ анализирует и выдает список задач
4. Отмечайте выполненное, отслеживайте прогресс

---

## 🚀 Текущий статус: Phase 1 (MVP UI) ✅

### Реализовано

#### ✅ Core UI & Models
- [x] SwiftData модели (`VideoProject`, `TaskItem`)
- [x] Главный Split View (Sidebar + Detail)
- [x] Список проектов с поиском
- [x] Детальный вид с чек-листом задач
- [x] Форма добавления видео (с валидацией URL)
- [x] Отслеживание прогресса (процент выполнения)
- [x] Экспорт в буфер обмена
- [x] Настройки (заглушка для API ключей)

#### 📐 Архитектура данных
```
VideoProject
├── id: UUID
├── title: String
├── youtubeUrl: String
├── videoId: String
├── thumbnailUrl: String?
├── createdAt: Date
├── updatedAt: Date
└── tasks: [TaskItem] (cascade delete)

TaskItem
├── id: UUID
├── title: String
├── details: String?
├── isCompleted: Bool
├── orderIndex: Int
├── completedAt: Date?
└── project: VideoProject?
```

---

## 📋 Roadmap

### Phase 2: AI Integration 🔜
- [ ] `APIService` для OpenAI/Anthropic
- [ ] System Prompt для генерации Action Plans
- [ ] Обработка JSON ответа от ИИ
- [ ] Mock режим для тестирования без API

### Phase 3: YouTube Logic 🔜
- [ ] Извлечение ID из URL ✅ (базово готово)
- [ ] Получение метаданных (Title, Thumbnail)
- [ ] Извлечение субтитров (timedtext API или альтернатива)
- [ ] Fallback: "Paste Transcript Mode"

### Phase 4: Polish & Export 🔜
- [ ] Обработка ошибок (нет субтитров, недоступно видео)
- [ ] Экспорт в Apple Notes
- [ ] Улучшенный UI/UX
- [ ] Иконка и брендинг

---

## 🛠️ Установка и запуск

### Требования
- **macOS 14.0 (Sonoma)** или новее
- **Xcode 15.0+**
- **Swift 5.9+**

### Шаг 1: Создание Xcode проекта

**Важно:** Swift Package Manager не поддерживает полноценные macOS GUI приложения. Нужен Xcode проект.

#### Вариант A: Создать вручную
1. Откройте Xcode
2. `File → New → Project`
3. Выберите `macOS → App`
4. Настройки:
   - **Product Name:** TubePlanner
   - **Interface:** SwiftUI
   - **Language:** Swift
   - **Storage:** SwiftData
5. Сохраните проект в папке `TubePlanner/`

#### Вариант B: Использовать существующие файлы
1. Создайте проект как в Варианте A
2. Удалите автогенерированные файлы (`ContentView.swift`, и т.д.)
3. Добавьте наши файлы в проект:
   - Перетащите папки `Models/`, `Views/`, `Services/` в Xcode
   - Убедитесь, что `TubePlannerApp.swift` на месте

### Шаг 2: Проверка файлов

Убедитесь, что в проекте есть:
```
TubePlanner/
├── TubePlannerApp.swift
├── Models/
│   ├── VideoProject.swift
│   └── TaskItem.swift
├── Views/
│   ├── ContentView.swift
│   ├── SidebarView.swift
│   ├── DetailView.swift
│   └── AddVideoView.swift
├── Services/
│   └── (пусто пока, для Phase 2)
└── Resources/
    └── (опционально: Assets, иконки)
```

### Шаг 3: Запуск
1. Нажмите `Cmd + R` для сборки и запуска
2. Если возникают ошибки:
   - Убедитесь, что выбран macOS deployment target 14.0+
   - Проверьте, что все файлы добавлены в target

---

## 🎨 Использование (Phase 1)

1. **Добавить видео:**
   - Нажмите `Cmd + N` или кнопку `+` в сайдбаре
   - Вставьте YouTube URL (поддерживаются `youtube.com/watch?v=...` и `youtu.be/...`)
   - Нажмите "Generate Action Plan"
   - *Примечание:* Сейчас создаются mock-задачи. Реальные задачи будут в Phase 2.

2. **Работать с задачами:**
   - Кликните по проекту в сайдбаре
   - Отмечайте задачи галочками
   - Прогресс сохраняется автоматически

3. **Экспорт:**
   - Нажмите кнопку "Export" в тулбаре
   - Выберите "Copy to Clipboard"
   - Задачи будут скопированы в формате Markdown

---

## 🏗️ Структура кода

### Models
- **VideoProject.swift** — основная модель проекта с computed properties (прогресс, счётчик задач)
- **TaskItem.swift** — модель задачи с методами `toggleCompletion()`, `complete()`, `uncomplete()`

### Views
- **ContentView.swift** — главный Split View контейнер
- **SidebarView.swift** — список проектов с поиском и статистикой
- **DetailView.swift** — детальный вид проекта с чек-листом
- **AddVideoView.swift** — форма добавления видео с валидацией URL

### Services (Phase 2+)
- Пока пусто, здесь будут:
  - `APIService.swift` — работа с OpenAI/Anthropic API
  - `YouTubeService.swift` — извлечение метаданных и субтитров
  - `TranscriptParser.swift` — обработка текста

---

## 🧪 Тестирование

### SwiftUI Previews
Каждый View имеет `#Preview` макросы для быстрой итерации:
- `ContentView` — с моковыми проектами и пустым состоянием
- `SidebarView` — с проектами и без
- `DetailView` — с полным списком задач
- `AddVideoView` — форма добавления

Используйте `Cmd + Option + P` в Xcode для запуска Previews.

---

## 🔑 Настройки API (Phase 2)

После реализации Phase 2, нужно будет добавить API ключ:

1. Откройте `Settings` (Cmd + ,)
2. Перейдите на вкладку "API Keys"
3. Выберите провайдера:
   - **OpenAI** (GPT-4o) — [получить ключ](https://platform.openai.com/api-keys)
   - **Anthropic** (Claude 3.5 Sonnet) — [получить ключ](https://console.anthropic.com/)
4. Введите API ключ (хранится в macOS Keychain)

---

## 📚 Технологии

| Компонент | Технология |
|-----------|------------|
| UI Framework | SwiftUI |
| Data Persistence | SwiftData |
| Networking | URLSession + Async/Await |
| AI Provider | OpenAI API / Anthropic API |
| Platform | macOS 14.0+ |
| Language | Swift 5.9+ |

---

## 🤝 Вклад в проект

Этот проект находится в активной разработке. Phase 1 (MVP UI) завершена, следующие шаги:

1. **Phase 2:** Интеграция с AI (OpenAI/Anthropic)
2. **Phase 3:** YouTube API для субтитров
3. **Phase 4:** Полировка и улучшения

---

## 📄 Лицензия

MIT License — используйте как хотите!

---

## 🐛 Известные ограничения (Phase 1)

- Задачи генерируются моково (3 шаблонных задачи)
- Заголовок видео не извлекается ("Untitled Video")
- Субтитры не обрабатываются
- Экспорт в Notes не реализован (только буфер обмена)

Эти ограничения будут устранены в последующих фазах.

---

**Создано с ❤️ для продуктивности**
