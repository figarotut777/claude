# QuickSpend - Quick Start Guide

## ⚡️ Быстрый старт

### 1. Открыть проект в Xcode

```bash
# В терминале:
cd QuickSpend
open -a Xcode
```

Затем в Xcode:
1. File → New → Project → macOS App
2. Назовите проект **QuickSpend**
3. Выберите **SwiftUI** + **SwiftData**
4. Создайте проект
5. Перетащите все файлы из папки `QuickSpend/QuickSpend/` в проект

### 2. Запустить приложение

Нажмите **Cmd+R** или кнопку ▶️ в Xcode

### 3. Использование

#### Базовый ввод:
```
50                    → $50 · Uncategorized
500 кофе              → $500 · кофе
1200 еда обед         → $1200 · еда · обед
```

#### Примеры с разными категориями:
```
300 такси             → Иконка: 🚗 car.fill
150 кофе              → Иконка: ☕ cup.and.saucer.fill
2000 еда ресторан     → Иконка: 🍴 fork.knife
50 метро              → Иконка: 🚊 tram.fill
5000 продукты запас   → Иконка: 🛒 cart.fill
```

## 📁 Файловая структура

```
QuickSpend/
├── README.md                          # Полная документация
├── IMPLEMENTATION_NOTES.md            # Архитектура и детали
├── QUICKSTART.md                      # Этот файл
├── .gitignore                         # Git ignore для Xcode
│
└── QuickSpend/                        # Исходный код
    ├── QuickSpendApp.swift            # ✅ Точка входа
    │
    ├── Models/                        # ✅ SwiftData модели
    │   ├── Transaction.swift
    │   └── Category.swift
    │
    ├── ViewModels/                    # ✅ Бизнес-логика
    │   └── BudgetViewModel.swift
    │
    ├── Views/                         # ✅ UI компоненты
    │   ├── ContentView.swift
    │   └── InputView.swift
    │
    └── Utils/                         # ✅ Утилиты
        ├── InputParser.swift          # Парсинг текста
        ├── CategoryIconMapper.swift   # Маппинг иконок
        └── InputParserTests.swift     # Тесты
```

## ✅ Что уже работает (Phase 1-2)

- ✅ **Модели SwiftData**: Transaction, Category
- ✅ **Парсинг текста**: Regex-based InputParser
- ✅ **Умные иконки**: Автоматический подбор SF Symbols
- ✅ **MVVM архитектура**: BudgetViewModel
- ✅ **UI компоненты**: ContentView, InputView
- ✅ **Визуализация**: Swift Charts для диаграмм
- ✅ **Автосохранение**: SwiftData автоматически сохраняет
- ✅ **Группировка**: По дням (Сегодня, Вчера, дата)
- ✅ **Удаление**: Swipe to delete
- ✅ **Тесты**: Unit tests для парсера

## 🧪 Запуск тестов

В файле `InputParserTests.swift` раскомментируйте:

```swift
// В конце файла:
InputParserTests.runTests()
```

Затем запустите приложение (Cmd+R) и откройте консоль (Cmd+Shift+Y).

Вы увидите:
```
🧪 Running InputParser tests...

✅ Only amount
   Input: '50'
   → 50.0 · Uncategorized

✅ Amount with category
   Input: '500 кофе'
   → 500.0 · кофе

✅ Amount with category and note
   Input: '1200 еда бизнес ланч'
   → 1200.0 · еда · бизнес ланч

...

✅ All tests completed!
```

## 🎯 Следующие шаги

### Если хотите улучшить парсер:

```swift
// В InputParser.swift добавьте более сложную логику:

// Поддержка валюты в тексте
"купил кофе за 500 рублей" → 500 · кофе

// Поддержка дат
"500 кофе вчера" → 500 · кофе (date: вчера)

// Поддержка математики
"200+300 еда" → 500 · еда
```

### Если хотите добавить новые категории:

Откройте `CategoryIconMapper.swift` и добавьте:

```swift
case _ where lowercased.contains("ваша_категория"):
    return "your.sf.symbol"
```

### Если хотите изменить дизайн:

Откройте `ContentView.swift` и измените:
- Цвета фона
- Размеры шрифтов
- Отступы
- Анимации

## 🐛 Частые проблемы

### Проблема: SwiftData ошибки
```
'@Model' requires macOS 14.0 or newer
```

**Решение:**
1. Xcode → Select Project
2. General → Deployment Info
3. Minimum Deployments: **macOS 14.0**

### Проблема: Парсер не распознает числа
```
Input: "500,50 кофе" → Ошибка
```

**Решение:** Парсер уже поддерживает запятые! Проверьте, что используете актуальный `InputParser.swift`.

### Проблема: Иконки не отображаются

**Решение:** Проверьте имена SF Symbols:
```bash
open -a "SF Symbols"
```

## 📚 Дополнительные ресурсы

- [README.md](README.md) - Полная документация
- [IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md) - Архитектурные детали
- [Apple SwiftData Docs](https://developer.apple.com/documentation/swiftdata)
- [Swift Charts](https://developer.apple.com/documentation/charts)
- [SF Symbols](https://developer.apple.com/sf-symbols/)

## 💬 Обратная связь

Если что-то не работает:
1. Проверьте версию Xcode (требуется Xcode 15+)
2. Проверьте версию macOS (требуется macOS 14.0+)
3. Пересоздайте проект заново следуя инструкциям в README.md

---

**Приятной разработки!** 🚀
