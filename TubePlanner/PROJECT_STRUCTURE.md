# 📐 TubePlanner — Структура проекта

## Обзор архитектуры

TubePlanner следует классической архитектуре SwiftUI приложений:

```
TubePlanner/
├── 📱 TubePlannerApp.swift       # Entry point, SwiftData setup
├── 📦 Models/                    # Data layer (SwiftData)
├── 🎨 Views/                     # UI layer (SwiftUI)
├── 🔧 Services/                  # Business logic (Phase 2+)
└── 📄 Resources/                 # Assets, plists, etc.
```

---

## 📂 Детальная структура

### 1. App Entry Point

**`TubePlannerApp.swift`**
```swift
@main
struct TubePlannerApp: App {
    let modelContainer: ModelContainer  // SwiftData container

    var body: some Scene {
        WindowGroup { ContentView() }
            .modelContainer(modelContainer)
        Settings { SettingsView() }
    }
}
```

**Ответственность:**
- Инициализация SwiftData `ModelContainer`
- Настройка главного окна (WindowGroup)
- Регистрация команд меню (⌘N для нового проекта)
- Настройка Settings window

---

### 2. Models (Data Layer)

#### `VideoProject.swift`

**Назначение:** Представление YouTube видео проекта с его Action Plan.

**Ключевые поля:**
- `id: UUID` — уникальный идентификатор
- `title: String` — название видео (из YouTube API)
- `youtubeUrl: String` — оригинальная ссылка
- `videoId: String` — извлеченный ID (для API запросов)
- `tasks: [TaskItem]` — связанные задачи (one-to-many)
- `createdAt / updatedAt: Date` — временные метки

**Computed Properties:**
- `progressPercentage: Double` — процент выполнения (0-100)
- `completedTasksCount: Int` — количество выполненных задач

**Методы:**
- `markAsUpdated()` — обновить timestamp (вызывается при изменении задач)

**SwiftData аннотации:**
```swift
@Model
final class VideoProject {
    @Relationship(deleteRule: .cascade, inverse: \TaskItem.project)
    var tasks: [TaskItem]
    // При удалении проекта, задачи удаляются автоматически (cascade)
}
```

---

#### `TaskItem.swift`

**Назначение:** Одна задача (шаг) в Action Plan.

**Ключевые поля:**
- `id: UUID` — уникальный идентификатор
- `title: String` — описание задачи
- `details: String?` — дополнительные детали (опционально)
- `isCompleted: Bool` — статус выполнения
- `orderIndex: Int` — порядок сортировки
- `completedAt: Date?` — когда выполнено
- `project: VideoProject?` — родительский проект (inverse relationship)

**Методы:**
- `toggleCompletion()` — переключить статус + обновить timestamp + пометить проект
- `complete()` — пометить как выполненное
- `uncomplete()` — снять пометку

**Conformance:**
```swift
extension TaskItem: Comparable {
    static func < (lhs: TaskItem, rhs: TaskItem) -> Bool {
        lhs.orderIndex < rhs.orderIndex
    }
}
```
Позволяет сортировать задачи: `tasks.sorted()`

---

### 3. Views (UI Layer)

#### `ContentView.swift`

**Назначение:** Главный контейнер с NavigationSplitView.

**Структура:**
```swift
NavigationSplitView {
    SidebarView(...)        // Sidebar с списком проектов
} detail: {
    if let selectedProject {
        DetailView(project: selectedProject)
    } else {
        ContentUnavailableView(...)  // Пустое состояние
    }
}
```

**State:**
- `@Query(sort: \VideoProject.createdAt)` — загрузка проектов из SwiftData
- `@State selectedProject: VideoProject?` — выбранный проект
- `@State showingAddVideoSheet: Bool` — контроль sheet'а для добавления видео

**Features:**
- Sheet для `AddVideoView`
- Слушает `NotificationCenter` для ⌘N (New Video)
- Preview containers (с данными и пустой)

---

#### `SidebarView.swift`

**Назначение:** Список проектов в сайдбаре.

**Структура:**
```swift
VStack {
    headerView              // Счетчик проектов
    if filteredProjects.isEmpty {
        emptyStateView      // "No Projects" state
    } else {
        List {
            ForEach(projects) { project in
                ProjectRowView(project: project)
            }
        }
    }
}
.searchable(text: $searchText)
```

**Features:**
- Поиск по названию видео (`.searchable`)
- Context menu для удаления
- Swipe-to-delete (`.onDelete`)
- Статистика: количество проектов
- Кнопка "+" в тулбаре

**Subviews:**
- `ProjectRowView` — строка с названием, прогрессом, датой

---

#### `DetailView.swift`

**Назначение:** Детальный вид проекта с чек-листом.

**Структура:**
```swift
ScrollView {
    VStack {
        headerSection       // Название, ссылка на YouTube
        progressSection     // Progress bar (0-100%)
        tasksSection        // Список задач
            ForEach(sortedTasks) { task in
                TaskRowView(task: task)
            }
    }
}
.toolbar {
    Menu("Export") { ... }
}
```

**Features:**
- Прогресс бар с цветами:
  - 0-25% → 🔴 Red
  - 25-50% → 🟠 Orange
  - 50-75% → 🟡 Yellow
  - 75-100% → 🔵 Blue
  - 100% → 🟢 Green
- Экспорт в Markdown
- Копирование в буфер обмена
- Ссылка на YouTube (открывается в браузере)

**Subviews:**
- `TaskRowView` — строка с checkbox, зачеркиванием, timestamp'ом

---

#### `AddVideoView.swift`

**Назначение:** Sheet для добавления нового видео.

**Структура:**
```swift
NavigationStack {
    VStack {
        headerView          // Иконка, заголовок
        urlInputSection     // TextField с валидацией
        instructionsSection // Как это работает (1-2-3-4)
        actionButtons       // Cancel / Generate
    }
}
.sheet(isPresented: $isPresented)
```

**Features:**
- Валидация YouTube URL (регулярные выражения)
- Поддержка форматов:
  - `youtube.com/watch?v=VIDEO_ID`
  - `youtu.be/VIDEO_ID`
  - `youtube.com/embed/VIDEO_ID`
- Keyboard shortcuts:
  - ⌘↩ — Generate
  - ⎋ — Cancel
- Loading state (Processing...)
- Error alerts

**Методы:**
- `extractVideoId(from url: String) -> String?` — парсинг URL
- `processVideo()` — создание проекта (сейчас mock, в Phase 2 — API)

---

### 4. Services (Business Logic)

**Статус:** Пока пусто (Phase 2+)

**Планируется:**

#### `APIService.swift`
```swift
class APIService {
    func generateActionPlan(from transcript: String) async throws -> [TaskItem]
    func callOpenAI(prompt: String) async throws -> OpenAIResponse
    func callAnthropic(prompt: String) async throws -> AnthropicResponse
}
```

#### `YouTubeService.swift`
```swift
class YouTubeService {
    func fetchMetadata(videoId: String) async throws -> VideoMetadata
    func fetchTranscript(videoId: String) async throws -> String
    func extractVideoId(from url: String) -> String?
}
```

#### `TranscriptParser.swift`
```swift
class TranscriptParser {
    func parseTimedText(xml: String) -> String
    func cleanTranscript(rawText: String) -> String
}
```

---

## 🔄 Data Flow

### 1. Создание нового проекта

```
User Action (⌘N)
    ↓
ContentView (showingAddVideoSheet = true)
    ↓
AddVideoView.sheet появляется
    ↓
User вводит URL → processVideo()
    ↓
extractVideoId() → валидация
    ↓
[Phase 2] YouTubeService.fetchMetadata()
    ↓
[Phase 2] YouTubeService.fetchTranscript()
    ↓
[Phase 2] APIService.generateActionPlan()
    ↓
VideoProject создается
    ↓
modelContext.insert(project) + save()
    ↓
@Query автоматически обновляется
    ↓
SidebarView показывает новый проект
```

### 2. Выполнение задачи

```
User кликает на checkbox
    ↓
TaskRowView: task.toggleCompletion()
    ↓
TaskItem.isCompleted.toggle()
TaskItem.completedAt = Date()
    ↓
project.markAsUpdated()
    ↓
SwiftData автоматически сохраняет
    ↓
@Bindable обновляет UI (withAnimation)
    ↓
ProgressSection пересчитывает progressPercentage
```

### 3. Экспорт в буфер обмена

```
User: Menu → "Copy to Clipboard"
    ↓
DetailView.exportToClipboard()
    ↓
generateExportText() → Markdown строка
    ↓
NSPasteboard.general.setString()
    ↓
Alert "Exported successfully"
```

---

## 🎨 Design Patterns

### 1. MVVM (Model-View-ViewModel)

**Model:** `VideoProject`, `TaskItem` (SwiftData)
**View:** `ContentView`, `SidebarView`, `DetailView`
**ViewModel:** Implicit (`@Query`, `@Bindable`, `@State`)

SwiftUI использует reactive bindings вместо явных ViewModels.

### 2. Dependency Injection

**SwiftData Container:**
```swift
TubePlannerApp.swift → .modelContainer(modelContainer)
    ↓
Views получают @Environment(\.modelContext)
```

**No manual DI framework needed** — SwiftUI Environment делает это автоматически.

### 3. Separation of Concerns

| Layer | Ответственность |
|-------|----------------|
| Models | Данные, бизнес-логика моделей |
| Views | UI, пользовательские действия |
| Services | Сетевые запросы, внешние API |

---

## 🧪 Testing Strategy (для будущего)

### Unit Tests
- Models:
  - `VideoProject.progressPercentage` работает корректно
  - `TaskItem.toggleCompletion()` обновляет timestamps
- Services:
  - `YouTubeService.extractVideoId()` корректно парсит URL
  - `APIService.generateActionPlan()` обрабатывает JSON

### UI Tests
- Создание проекта (end-to-end)
- Выполнение всех задач → прогресс 100%
- Экспорт → проверка clipboard

### Preview Tests
- SwiftUI Previews для визуального тестирования
- Mock data containers

---

## 📝 Coding Conventions

### Naming

```swift
// Models: UpperCamelCase
class VideoProject { }
class TaskItem { }

// Properties: lowerCamelCase
var youtubeUrl: String
var isCompleted: Bool

// Methods: lowerCamelCase + verb
func markAsUpdated()
func toggleCompletion()

// Views: UpperCamelCase + "View" suffix
struct ContentView: View { }
struct SidebarView: View { }
```

### Comments

```swift
// MARK: - Properties        // Разделы класса
// MARK: Computed Properties  // Подразделы (без -)

/// Doc comment для публичных API
/// - Parameter url: YouTube URL to parse
func extractVideoId(from url: String) -> String?
```

### SwiftUI Style

```swift
// Preferred
Text("Hello")
    .font(.headline)
    .foregroundStyle(.blue)

// Avoid
Text("Hello").font(.headline).foregroundStyle(.blue)
```

---

## 🔧 Configuration Files

### `Package.swift`
- Определяет зависимости (пока пусто)
- Platform: macOS 14.0+
- Swift 5.9+

### `Info.plist`
- Bundle ID, версия
- App Transport Security (для YouTube API)
- Category: Productivity

---

## 📊 Metrics (Phase 1)

| Metric | Value |
|--------|-------|
| **Lines of Code** | ~1200 |
| **Files** | 10 Swift files |
| **Models** | 2 (VideoProject, TaskItem) |
| **Views** | 5 (+ 3 subviews) |
| **Services** | 0 (Phase 2) |
| **Dependencies** | 0 (только stdlib + SwiftUI) |
| **Min macOS** | 14.0 (Sonoma) |

---

**Готово к Phase 2! 🚀**
