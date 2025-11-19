# 🚀 TubePlanner — Инструкция по настройке проекта

## Метод 1: Создать Xcode проект вручную (Рекомендуется)

### Шаг 1: Создайте новый проект в Xcode

1. Откройте Xcode 15.0 или новее
2. Выберите **File → New → Project** (⇧⌘N)
3. Выберите **macOS → App**
4. Нажмите **Next**

### Шаг 2: Настройте проект

Заполните следующие поля:

- **Product Name:** `TubePlanner`
- **Team:** Ваша команда или "None"
- **Organization Identifier:** `com.yourname` (любой идентификатор)
- **Bundle Identifier:** Автоматически сгенерируется
- **Interface:** `SwiftUI` ✅
- **Language:** `Swift` ✅
- **Storage:** `SwiftData` ✅
- **Include Tests:** По желанию (можно снять галочку для Phase 1)

Нажмите **Next**, выберите папку `claude/TubePlanner/` и создайте проект.

### Шаг 3: Удалите автогенерированные файлы

Xcode создаст несколько файлов, которые нам не нужны. Удалите:

- `ContentView.swift` (у нас есть своя версия)
- Любые другие `.swift` файлы, кроме `TubePlannerApp.swift` (если он был создан не нами)

**Важно:** Не удаляйте `Assets.xcassets` и другие ресурсы.

### Шаг 4: Добавьте наши файлы в проект

#### 4.1. Добавьте `TubePlannerApp.swift`

Если Xcode создал свой `TubePlannerApp.swift`:
1. Откройте его
2. Замените содержимое на наш файл `/TubePlanner/TubePlannerApp.swift`

Если файла нет:
1. Перетащите `/TubePlanner/TubePlannerApp.swift` в проект

#### 4.2. Добавьте папки с кодом

В Xcode, в левой панели Project Navigator:

1. **Создайте группу "Models":**
   - ПКМ на `TubePlanner` → **New Group** → Назовите `Models`
   - Перетащите файлы из `/TubePlanner/Models/` в эту группу:
     - `VideoProject.swift`
     - `TaskItem.swift`

2. **Создайте группу "Views":**
   - ПКМ на `TubePlanner` → **New Group** → Назовите `Views`
   - Перетащите файлы из `/TubePlanner/Views/`:
     - `ContentView.swift`
     - `SidebarView.swift`
     - `DetailView.swift`
     - `AddVideoView.swift`

3. **Создайте группу "Services":**
   - ПКМ на `TubePlanner` → **New Group** → Назовите `Services`
   - Пока пустая (для Phase 2)

При перетаскивании убедитесь, что выбраны:
- ✅ **Copy items if needed**
- ✅ **Create groups** (не folder references)
- ✅ **Add to targets: TubePlanner**

### Шаг 5: Настройте Build Settings

1. Выберите проект в Project Navigator (верхний элемент)
2. Выберите Target `TubePlanner`
3. Перейдите на вкладку **General**:
   - **Minimum Deployments:** macOS 14.0 или выше
4. Перейдите на вкладку **Build Settings**:
   - Найдите **Swift Language Version**
   - Убедитесь, что выбрано **Swift 5** или новее

### Шаг 6: Запустите проект

1. Нажмите **⌘R** (Product → Run)
2. Если появляются ошибки компиляции:
   - Проверьте, что все файлы добавлены в target
   - Убедитесь, что SwiftData включен
   - Проверьте, что macOS deployment target 14.0+

3. Если всё прошло успешно:
   - Откроется окно TubePlanner
   - Попробуйте создать проект (⌘N)
   - Вставьте любую YouTube ссылку
   - Увидите mock-задачи

---

## Метод 2: Использовать Xcode project file (альтернативный)

Если вы хотите создать `.xcodeproj` файл вручную через командную строку:

```bash
cd TubePlanner
swift package init --type executable --name TubePlanner
```

**Однако:** Swift Package Manager не поддерживает SwiftUI приложения с ресурсами напрямую. Поэтому **Метод 1** предпочтительнее.

---

## Проверка установки

После запуска приложения проверьте:

### ✅ Основной UI
- [ ] Окно открывается (минимум 800x600)
- [ ] Виден Split View: слева Sidebar, справа пустое состояние
- [ ] Кнопка "+" в тулбаре работает

### ✅ Создание проекта
- [ ] Нажмите **⌘N** или кнопку "+"
- [ ] Откроется форма "New Video Project"
- [ ] Введите: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- [ ] Нажмите "Generate Action Plan"
- [ ] Проект появится в сайдбаре

### ✅ Работа с задачами
- [ ] Выберите проект из списка
- [ ] Увидите 3 mock-задачи
- [ ] Кликните на checkbox — задача зачеркивается
- [ ] Прогресс обновляется (33% → 66% → 100%)

### ✅ Экспорт
- [ ] Нажмите кнопку "Export" в тулбаре
- [ ] Выберите "Copy to Clipboard"
- [ ] Откройте TextEdit, вставьте ⌘V
- [ ] Увидите Markdown чек-лист

### ✅ Персистентность
- [ ] Закройте приложение
- [ ] Запустите снова
- [ ] Проекты сохранились (SwiftData работает)

---

## Типичные проблемы

### ❌ Ошибка: "Cannot find 'VideoProject' in scope"

**Причина:** Файлы моделей не добавлены в target.

**Решение:**
1. Выберите файл `VideoProject.swift` в Project Navigator
2. В правой панели File Inspector проверьте **Target Membership**
3. Убедитесь, что галочка напротив `TubePlanner` стоит
4. Повторите для всех `.swift` файлов

---

### ❌ Ошибка: "Deployment target is earlier than 14.0"

**Причина:** Неправильно настроен minimum deployment target.

**Решение:**
1. Project → Target → General
2. **Minimum Deployments → macOS:** измените на 14.0

---

### ❌ Приложение не запускается, черный экран

**Причина:** `TubePlannerApp.swift` не настроен как @main entry point.

**Решение:**
1. Откройте `TubePlannerApp.swift`
2. Убедитесь, что есть `@main` перед `struct TubePlannerApp`
3. Проверьте, что только ОДИН файл в проекте имеет `@main`

---

### ❌ SwiftData ошибки при запуске

**Причина:** Schema не синхронизирована с моделями.

**Решение:**
1. Удалите приложение из `/Applications/`
2. Очистите build folder: **Product → Clean Build Folder** (⇧⌘K)
3. Перезапустите: **⌘R**

---

## Следующие шаги

После успешной настройки:

1. **Изучите код:**
   - Откройте `Models/VideoProject.swift` — посмотрите SwiftData аннотации
   - Откройте `Views/ContentView.swift` — изучите NavigationSplitView
   - Попробуйте SwiftUI Previews (**⌥⌘P**)

2. **Подготовьтесь к Phase 2:**
   - Зарегистрируйтесь на [OpenAI Platform](https://platform.openai.com/)
   - Получите API ключ (будет нужен для интеграции AI)
   - Изучите [OpenAI Chat API Docs](https://platform.openai.com/docs/api-reference/chat)

3. **Фидбек:**
   - Если нашли баги или есть идеи — создайте Issue в репозитории
   - Готовы к Phase 2? Дайте знать!

---

**Удачи! 🚀**
