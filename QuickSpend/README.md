# QuickSpend - Minimalist macOS Budget Tracker

> "Spotlight для денег" - быстрый трекинг расходов для macOS

## 📋 Обзор

QuickSpend - это нативное macOS-приложение для учета расходов с фокусом на скорость ввода. Просто введите "500 кофе" и нажмите Enter - приложение само распознает сумму и категорию.

### Ключевые особенности

- ⚡️ **Быстрый ввод**: Парсинг строк формата `[Сумма] [Категория] [Комментарий]`
- 🎨 **Умные иконки**: Автоматический подбор SF Symbols иконок для категорий
- 📊 **Визуализация**: Круговая диаграмма расходов по категориям
- 💾 **SwiftData**: Современное хранилище данных
- 🎯 **Минимализм**: Чистый интерфейс без лишних форм

## 🛠 Технический стек

- **Язык**: Swift 5.9+
- **UI**: SwiftUI
- **Платформа**: macOS 14.0 (Sonoma) и новее
- **Хранение данных**: SwiftData
- **Графики**: Swift Charts
- **Архитектура**: MVVM

## 📁 Структура проекта

```
QuickSpend/
├── QuickSpendApp.swift          # Точка входа, настройка ModelContainer
├── Models/
│   ├── Transaction.swift        # Модель транзакции
│   └── Category.swift          # Модель категории
├── ViewModels/
│   └── BudgetViewModel.swift   # Бизнес-логика и состояние
├── Views/
│   ├── ContentView.swift       # Главное окно с дашбордом
│   └── InputView.swift         # Компонент быстрого ввода
└── Utils/
    ├── InputParser.swift       # Парсинг текстового ввода
    ├── CategoryIconMapper.swift # Маппинг категорий → иконки
    └── InputParserTests.swift  # Тесты для парсера
```

## 🚀 Настройка проекта в Xcode

### Шаг 1: Создать новый проект

1. Откройте Xcode
2. File → New → Project
3. Выберите **macOS** → **App**
4. Настройки:
   - **Product Name**: QuickSpend
   - **Interface**: SwiftUI
   - **Storage**: SwiftData
   - **Language**: Swift
   - **Minimum Deployment**: macOS 14.0

### Шаг 2: Добавить файлы

1. Удалите автоматически созданные файлы (кроме `Assets.xcassets`)
2. Перетащите все файлы из директории `QuickSpend/` в проект
3. Убедитесь, что файлы добавлены в правильные группы:
   - Models → `Transaction.swift`, `Category.swift`
   - ViewModels → `BudgetViewModel.swift`
   - Views → `ContentView.swift`, `InputView.swift`
   - Utils → `InputParser.swift`, `CategoryIconMapper.swift`, `InputParserTests.swift`

### Шаг 3: Запустить проект

1. Выберите схему **QuickSpend**
2. Нажмите **Cmd+R** для запуска
3. Приложение откроется в отдельном окне

## 🧪 Тестирование парсера

В файле `InputParserTests.swift` раскомментируйте последнюю строку:

```swift
InputParserTests.runTests()
```

Затем запустите приложение и проверьте консоль - вы увидите результаты всех тестов.

### Примеры парсинга

| Ввод | Сумма | Категория | Комментарий |
|------|-------|-----------|-------------|
| `50` | 50 | Uncategorized | - |
| `500 кофе` | 500 | кофе | - |
| `1200 еда бизнес ланч` | 1200 | еда | бизнес ланч |
| `99.50 такси` | 99.50 | такси | - |
| `5000 продукты недельный запас` | 5000 | продукты | недельный запас |

## 🎨 Автоматические иконки

Приложение автоматически подбирает иконки SF Symbols для категорий:

- **Еда** → `fork.knife`
- **Кофе** → `cup.and.saucer.fill`
- **Такси** → `car.fill`
- **Транспорт** → `car`
- **Развлечения** → `party.popper.fill`
- **Покупки** → `bag.fill`
- **Здоровье** → `heart.fill`
- **Спорт** → `figure.run`
- И многие другие...

## ⌨️ Горячие клавиши

- **Cmd+N** - Фокус на поле ввода
- **Enter** - Сохранить транзакцию
- **Swipe left** на транзакции - Удалить

## 🔧 Возможные проблемы

### SwiftData ошибки компиляции

Если вы видите ошибки типа:
```
'@Model' requires macOS 14.0 or newer
```

**Решение**: Проверьте минимальную версию в настройках проекта:
1. Выберите проект в навигаторе
2. General → Deployment Info
3. Установите **Minimum Deployments: macOS 14.0**

### Парсер работает некорректно

**Решение**: Откройте `InputParser.swift` и улучшите логику регулярных выражений:

```swift
// Используйте более сложные регулярки для точного парсинга
let numberPattern = #"(\d+(?:[.,]\d+)?)"#
```

### Иконки не отображаются

**Решение**: Проверьте, что используются валидные имена SF Symbols. Открыть SF Symbols app:
```bash
open -a "SF Symbols"
```

## 📦 Phase 1 & 2 - Готово! ✅

- ✅ Foundation: Модели SwiftData, ModelContainer
- ✅ Logic Engine: InputParser с regex-логикой
- ✅ Category Icon Mapper: Автоматический подбор иконок
- ✅ Basic UI: InputView, ContentView, BudgetViewModel
- ✅ Тесты: InputParserTests

## 🎯 Следующие шаги (Phase 3-4)

После того, как проект откроется в Xcode и скомпилируется:

### Phase 3: Basic UI Enhancement
- Добавить анимации при добавлении транзакций
- Улучшить дизайн с градиентами и тенями
- Добавить звуковые эффекты

### Phase 4: Visualization & Polish
- Добавить фильтры (по дате, категории)
- Экспорт данных (CSV, Excel)
- Настройки приложения
- Dark Mode поддержка

## 📝 Лицензия

MIT

## 👨‍💻 Автор

Created with ❤️ by Claude
