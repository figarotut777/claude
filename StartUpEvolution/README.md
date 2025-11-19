# StartUp Evolution — AI-Powered Clicker Game

Нативное macOS-приложение "кликер" (idle game), в котором игрок развивает виртуальный стартап от гаража до статуса единорога.

## Технический стек

- **Язык:** Swift 5.9+
- **UI Фреймворк:** SwiftUI
- **Платформа:** macOS 14.0+ (Sonoma)
- **Архитектура:** MVVM
- **Хранение:** UserDefaults

## Текущий статус: Phase 1 (Game Core & UI) ✅

### Реализовано:

- ✅ GameViewModel с логикой управления деньгами, XP и уровнями
- ✅ Основной UI: кнопка "Code", счетчики, прогресс-бар
- ✅ Сохранение и загрузка прогресса через UserDefaults
- ✅ Система уровней (5 стадий: от Garage до Unicorn)
- ✅ CTA модальное окно при достижении Unicorn Status
- ✅ Динамические фоновые градиенты для каждой стадии
- ✅ Placeholder для логотипа (готово к Phase 2)

### Следующие этапы:

- **Phase 2:** DALL-E 3 интеграция для генерации логотипов
- **Phase 3:** Stage Progression & Logo Generation Logic
- **Phase 4:** Звуки, анимации, полировка

## Запуск проекта

### Требования:

- macOS 14.0+ (Sonoma)
- Xcode 15.0+
- Swift 5.9+

### Сборка и запуск:

```bash
cd StartUpEvolution

# Открыть в Xcode (автоматически создаст .xcodeproj)
open Package.swift

# Или собрать через Swift Package Manager
swift build

# Запустить приложение
swift run
```

## Игровая механика

### Основной loop:

1. Нажимаешь кнопку **"< CODE />"**
2. Получаешь +$1 и +1 XP
3. При достижении порога XP переходишь на новый уровень
4. Фон и логотип обновляются
5. При достижении 501+ XP (Unicorn Status) появляется CTA

### Уровни компании:

1. **Garage Startup** (0-50 XP)
2. **Small Office** (51-150 XP)
3. **Co-Working Space** (151-300 XP)
4. **Mid-size Company** (301-500 XP)
5. **Unicorn Status** (501+ XP) — триггер CTA

## Структура проекта

```
StartUpEvolution/
├── Package.swift
├── README.md
└── Sources/
    └── StartUpEvolution/
        ├── StartUpEvolutionApp.swift    # Entry point
        ├── Models/
        │   └── GameStage.swift          # Enum для стадий
        ├── ViewModels/
        │   └── GameViewModel.swift      # MVVM логика + UserDefaults
        ├── Views/
        │   └── ContentView.swift        # Main UI
        └── Services/
            └── (APIService.swift)       # Phase 2
```

## Debug функции

В приложении есть debug кнопки для тестирования:

- **Add 50 XP** — быстро прокачать уровень
- **Reset Game** — сбросить прогресс

## Архитектура

### MVVM Pattern:

- **Model:** `GameStage` (enum с данными о стадиях)
- **ViewModel:** `GameViewModel` (бизнес-логика, состояние игры)
- **View:** `ContentView` (UI, биндинги к ViewModel)

### Persistence:

Данные сохраняются в `UserDefaults`:

- `money`: Int
- `xp`: Int
- `currentStage`: String
- `currentLogoPath`: String?
- `hasShownCTA`: Bool

## Лицензия

Проект создан в образовательных целях.

## Контакты

Для вопросов создавайте issue в репозитории.
