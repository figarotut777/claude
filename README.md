# LA-2A Optical Compressor Plugin

Высококачественный плагин оптического компрессора, смоделированный по образцу легендарного Teletronix LA-2A. Этот плагин точно воспроизводит характерное звучание оригинала благодаря детальному моделированию оптоэлектронной цепи, лампового каскада и трансформаторов.

## Основные возможности

### Аутентичное моделирование LA-2A

- **Оптическая ячейка (Opto-Cell)**: Точное моделирование T4B оптоэлектронного аттенюатора с нелинейным временем отклика
- **Многоступенчатый Release**: Характерная двухфазная кривая восстановления (быстрый начальный сброс + медленный хвост)
- **Нелинейный Attack**: Время атаки зависит от амплитуды входного сигнала (1-10ms)
- **Ламповое насыщение**: Моделирование входного и выходного ламповых каскадов (12AX7/ECC83)
- **Трансформаторы**: Генерация 2-й и 3-й гармоник с гистерезисом магнитного сердечника
- **4x оверсэмплинг**: Минимизация алиасинга от нелинейных процессов

### Управление

- **Peak Reduction** (0-100%): Контролирует пороговый уровень и степень компрессии
- **Gain** (-20 до +20 dB): Make-up gain для компенсации снижения уровня
- **Compress/Limit**: Переключатель режимов
  - Compress: Мягкая компрессия с ratio ~3:1
  - Limit: Жесткое ограничение с ratio ~100:1
- **VU Meter**: Визуальное отображение Gain Reduction

## Сборка проекта

### Требования

- CMake 3.22 или выше
- JUCE Framework 7.0+ (https://github.com/juce-framework/JUCE)
- C++17 совместимый компилятор
  - Windows: Visual Studio 2019 или новее
  - macOS: Xcode 12 или новее
  - Linux: GCC 9+ или Clang 10+

### Установка JUCE

#### Вариант 1: Автоматическая загрузка (рекомендуется)

Раскомментируйте секцию FetchContent в `CMakeLists.txt`:

```cmake
include(FetchContent)
FetchContent_Declare(
    JUCE
    GIT_REPOSITORY https://github.com/juce-framework/JUCE.git
    GIT_TAG 7.0.9
)
FetchContent_MakeAvailable(JUCE)
```

#### Вариант 2: Установка вручную

```bash
git clone https://github.com/juce-framework/JUCE.git
cd JUCE
git checkout 7.0.9
```

Затем в `CMakeLists.txt` укажите путь:

```cmake
set(JUCE_DIR "/path/to/JUCE" CACHE PATH "Path to JUCE")
add_subdirectory(${JUCE_DIR} JUCE)
```

### Компиляция

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd claude

# Создайте директорию для сборки
mkdir build
cd build

# Конфигурация CMake
cmake ..

# Компиляция
cmake --build . --config Release

# Плагин будет создан в:
# - Windows: build/LA2ACompressor_artefacts/Release/VST3/
# - macOS: build/LA2ACompressor_artefacts/Release/VST3/ или AU/
# - Linux: build/LA2ACompressor_artefacts/Release/VST3/
```

## Технические детали

### Сигнальная цепь

```
Input Signal
    ↓
Input Transformer (harmonic generation, frequency shaping)
    ↓
Input Tube Stage (12AX7, soft saturation)
    ↓
Level Detection (RMS with fast attack/slow release)
    ↓
Opto-Cell Processing (T4B cell emulation)
    ↓
Gain Reduction Application
    ↓
Output Tube Stage (harmonic enhancement)
    ↓
Output Transformer (final coloration)
    ↓
Make-up Gain
    ↓
Output Signal
```

### Оптическая ячейка (OptoCell)

Ключевой элемент LA-2A, моделирует взаимодействие светодиода и фоторезистора:

- **Нелинейное время Attack**: 1-10ms в зависимости от входного уровня
- **Двухфазный Release**:
  - Быстрая фаза: ~60ms (начальный сброс)
  - Медленная фаза: ~2s (долгий хвост)
  - Blend: 70% быстрой + 30% медленной фазы
- **Логарифмическая характеристика**: Имитация нелинейности фотодиода

### Ламповое насыщение

Моделирование триода (12AX7/ECC83):

- Асимметричное ограничение для генерации четных гармоник
- Tanh-based передаточная характеристика
- Кубическая нелинейность для 3-й гармоники
- DC blocker для удаления постоянной составляющей

### Трансформаторы

Входной и выходной трансформаторы добавляют характерную окраску:

- Насыщение магнитного сердечника (генерация гармоник)
- Гистерезис для реалистичности
- Low-shelf boost на ~100Hz (+1dB)
- High-frequency roll-off на ~15kHz (-3dB)

### Оверсэмплинг

4x оверсэмплинг (2 stages) с использованием JUCE DSP:

- Half-band polyphase IIR фильтры
- Минимизация алиасинга от нелинейных процессов
- Автоматическая компенсация латентности

## Использование

### Основные приемы

1. **Вокальная компрессия**
   - Peak Reduction: 30-50%
   - Gain: +2 до +6 dB
   - Mode: Compress

2. **Бас и барабаны**
   - Peak Reduction: 40-70%
   - Gain: +4 до +8 dB
   - Mode: Compress или Limit

3. **Мастеринг (glue compression)**
   - Peak Reduction: 10-25%
   - Gain: 0 до +3 dB
   - Mode: Compress

4. **Limiting**
   - Peak Reduction: 60-90%
   - Gain: настройте по вкусу
   - Mode: Limit

### Советы по использованию

- LA-2A имеет медленный attack, поэтому пропускает транзиенты - отлично для сохранения панча
- Длинный release создает эффект "дыхания", особенно заметный на басу и вокале
- Используйте умеренные значения Peak Reduction для тонкого контроля динамики
- В режиме Limit плагин становится агрессивным ограничителем
- Благодаря гармоническим искажениям, звук становится более насыщенным и "теплым"

## Структура проекта

```
claude/
├── CMakeLists.txt              # Конфигурация сборки
├── README.md                   # Документация
└── Source/
    ├── PluginProcessor.h       # Главный процессор
    ├── PluginProcessor.cpp
    ├── PluginEditor.h          # GUI
    ├── PluginEditor.cpp
    └── DSP/
        ├── OptoCell.h          # Моделирование оптической ячейки
        ├── OptoCell.cpp
        ├── TubeSaturation.h    # Ламповое насыщение
        ├── TubeSaturation.cpp
        ├── TransformerModel.h  # Трансформаторы
        ├── TransformerModel.cpp
        ├── Oversampling.h      # 4x оверсэмплинг
        └── Oversampling.cpp
```

## Лицензия

Этот проект создан в образовательных целях. Используйте его на свой страх и риск.

## Благодарности

Основан на документации и анализе оригинального Teletronix LA-2A и современных эмуляций.

## Контакты

Для вопросов и предложений создавайте issue в репозитории проекта.