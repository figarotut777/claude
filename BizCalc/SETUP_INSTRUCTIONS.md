# 🚀 Setup Instructions - BizCalc для macOS

## Быстрый старт

### Шаг 1: Создание Xcode проекта

1. Откройте **Xcode** (версия 15+)

2. **File → New → Project** (или ⇧⌘N)

3. Выберите шаблон:
   - Вкладка: **macOS**
   - Тип: **App**
   - Нажмите **Next**

4. Настройки проекта:
   ```
   Product Name:        BizCalc
   Team:                [Ваша команда или None]
   Organization ID:     com.yourcompany
   Bundle Identifier:   com.yourcompany.BizCalc
   Interface:           SwiftUI
   Language:            Swift
   Use Core Data:       ❌ (не отмечать)
   Include Tests:       ✅ (отметить)
   ```

5. Выберите папку для сохранения (можно удалить автосозданные файлы)

6. Deployment Info:
   - macOS 13.0 или выше

### Шаг 2: Импорт файлов

#### Метод 1: Перетаскивание (Drag & Drop)

1. В Finder откройте папку `BizCalc/BizCalc/`
2. Перетащите папки в Xcode Navigator:
   - **App** → в корень проекта
   - **Models** → в корень проекта
   - **ViewModels** → в корень проекта
   - **Views** → в корень проекта
   - **Tests/FormulaTests.swift** → в группу Tests

3. При добавлении убедитесь:
   - ✅ Copy items if needed
   - ✅ Create groups
   - ✅ Add to targets: BizCalc

#### Метод 2: Через Xcode (Add Files)

1. Правый клик на группе `BizCalc` → **Add Files to "BizCalc"...**
2. Выберите папки: `App`, `Models`, `ViewModels`, `Views`
3. Опции:
   - ✅ Copy items if needed
   - ⚪ Create groups (не folders)
   - Target: BizCalc

### Шаг 3: Настройка проекта

#### 3.1. Удалите автосозданный файл (если есть)
- `ContentView.swift` в корне (не тот, что в Views/)
- `BizCalcApp.swift` в корне (если был создан)

#### 3.2. Проверьте структуру в Project Navigator:
```
BizCalc/
├── 📁 App
│   └── BizCalcApp.swift
├── 📁 Models
│   ├── CalculatorEngine.swift
│   └── HistoryItem.swift
├── 📁 ViewModels
│   └── CalculatorViewModel.swift
├── 📁 Views
│   ├── ContentView.swift
│   ├── CalculatorButtonsView.swift
│   └── HistoryView.swift
└── 📁 Assets.xcassets (автосоздан)

BizCalcTests/
└── FormulaTests.swift
```

#### 3.3. Настройте минимальную версию macOS

1. Выберите проект в Navigator (синяя иконка вверху)
2. Target: **BizCalc**
3. General → Deployment Info
4. **Minimum Deployments**: macOS 13.0

### Шаг 4: Запуск

1. Выберите схему: **BizCalc** > **My Mac**
2. Нажмите **Run** (▶️) или **⌘R**

Приложение должно запуститься! 🎉

### Шаг 5: Запуск тестов (опционально)

1. **Product → Test** (или ⌘U)
2. Все тесты должны пройти успешно ✅

## 🔍 Проверка работоспособности

### Тест 1: MARGIN (Маржа)
```
Ввод: 100
Кнопка: MARGIN
Ввод: 20
Кнопка: =
Результат: 125 ✅
```

### Тест 2: MARKUP (Наценка)
```
AC
Ввод: 100
Кнопка: MARKUP
Ввод: 20
Кнопка: =
Результат: 120 ✅
```

### Тест 3: TAX+ (Налог)
```
AC
Ввод: 1000
Кнопка: TAX+
Ввод: 20
Кнопка: =
Результат: 1200 ✅
```

## ⚠️ Возможные проблемы

### Ошибка: "Cannot find 'BizCalcApp' in scope"
**Решение:** Убедитесь, что файл `BizCalcApp.swift` имеет `@main` атрибут и находится в target BizCalc.

### Ошибка: "Multiple commands produce..."
**Решение:**
1. File → Project Settings
2. Build System → New Build System
3. Clean Build Folder (⇧⌘K)

### Ошибка: Import не работает в тестах
**Решение:**
1. Выберите `FormulaTests.swift`
2. File Inspector (справа) → Target Membership
3. ✅ Убедитесь, что отмечен `BizCalcTests`

### Окно не отображается правильно
**Решение:**
1. Проверьте версию macOS (нужна 13.0+)
2. Очистите derived data: `⇧⌘K` (Clean Build Folder)

## 📦 Опциональные улучшения

### Добавить иконку приложения

1. Создайте иконку 1024x1024px
2. Перетащите в `Assets.xcassets → AppIcon`
3. Или используйте [SF Symbols](https://developer.apple.com/sf-symbols/) app

### Настроить сборку Release

1. Product → Scheme → Edit Scheme
2. Run → Build Configuration → Release
3. Archive для дистрибуции

### Создать .dmg для распространения

```bash
# После архивирования в Xcode
# Product → Archive → Distribute App → Developer ID
```

## 🎨 Кастомизация

### Изменить цвета кнопок
Файл: `CalculatorButtonsView.swift`
```swift
// Найдите var buttonBackground
case .operation:
    Color.blue.opacity(0.5) // Измените на свой цвет
```

### Изменить процент налога по умолчанию
Файл: `CalculatorEngine.swift`
```swift
@Published var taxRate: Double = 20.0 // Измените на нужный
```

## 📚 Дополнительные ресурсы

- [SwiftUI Documentation](https://developer.apple.com/documentation/swiftui)
- [SF Symbols](https://developer.apple.com/sf-symbols/)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/macos)

## 🤝 Поддержка

Если возникли проблемы:
1. Убедитесь, что используете Xcode 15+ и macOS 13+
2. Проверьте, что все файлы добавлены в правильный Target
3. Попробуйте Clean Build (⇧⌘K) и перезапуск Xcode

---

**Готово!** Теперь у вас есть полнофункциональный бизнес-калькулятор! 🚀
