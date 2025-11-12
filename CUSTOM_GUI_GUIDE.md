# Руководство по добавлению кастомного дизайна

## Обзор

Этот документ объясняет, как интегрировать твой собственный графический дизайн в плагин LA-2A.

## Подход 1: Image-Based GUI (Рекомендуется)

Это самый простой и эффективный метод для создания красивого винтажного дизайна.

### Шаг 1: Подготовь графику

Создай следующие изображения в Photoshop/Figma/etc:

1. **Background.png** (500x400px) - Основной фон плагина
   - Металлическая панель
   - Текстуры, винты, надписи
   - VU-метр (фон)

2. **Knob_PeakReduction.png** (100x100px x 64 кадра = 6400px высотой)
   - Фильмстрип анимации ручки Peak Reduction
   - 64 кадра вращения от 0° до 300°

3. **Knob_Gain.png** (80x80px x 64 кадра = 5120px высотой)
   - Фильмстрип для ручки Gain

4. **Switch_Compress.png** и **Switch_Limit.png** (50x30px)
   - Два состояния переключателя

5. **LED_On.png** и **LED_Off.png** (20x20px)
   - Индикатор Stereo Link

6. **VUMeter_Needle.png** (150x10px)
   - Стрелка VU-метра

### Шаг 2: Добавь ресурсы в проект

```cmake
# В CMakeLists.txt добавь:
juce_add_binary_data(LA2AResources SOURCES
    Resources/Background.png
    Resources/Knob_PeakReduction.png
    Resources/Knob_Gain.png
    Resources/Switch_Compress.png
    Resources/Switch_Limit.png
    Resources/LED_On.png
    Resources/LED_Off.png
    Resources/VUMeter_Needle.png
)

target_link_libraries(LA2ACompressor
    PRIVATE
        LA2AResources  # Добавь эту строку
        juce::juce_audio_utils
        ...
)
```

### Шаг 3: Создай кастомный LookAndFeel

Создай файл `Source/GUI/CustomLookAndFeel.h`:

```cpp
#pragma once

#include <juce_gui_basics/juce_gui_basics.h>

class LA2ALookAndFeel : public juce::LookAndFeel_V4
{
public:
    LA2ALookAndFeel()
    {
        // Загружаем изображения из BinaryData
        knobPeakReduction = juce::ImageCache::getFromMemory(
            BinaryData::Knob_PeakReduction_png,
            BinaryData::Knob_PeakReduction_pngSize
        );

        knobGain = juce::ImageCache::getFromMemory(
            BinaryData::Knob_Gain_png,
            BinaryData::Knob_Gain_pngSize
        );
    }

    void drawRotarySlider(juce::Graphics& g, int x, int y, int width, int height,
                         float sliderPos, float rotaryStartAngle, float rotaryEndAngle,
                         juce::Slider& slider) override
    {
        // Определяем какую ручку рисовать
        juce::Image knobImage = (&slider == peakReductionSlider)
                                ? knobPeakReduction
                                : knobGain;

        if (knobImage.isValid())
        {
            const int numFrames = 64;
            const int frameHeight = knobImage.getHeight() / numFrames;
            const int frameIndex = (int)(sliderPos * (numFrames - 1));

            g.drawImage(knobImage,
                       x, y, width, height,
                       0, frameIndex * frameHeight,
                       knobImage.getWidth(), frameHeight);
        }
    }

    void setSliders(juce::Slider* peak, juce::Slider* gain)
    {
        peakReductionSlider = peak;
        gainSlider = gain;
    }

private:
    juce::Image knobPeakReduction;
    juce::Image knobGain;
    juce::Slider* peakReductionSlider = nullptr;
    juce::Slider* gainSlider = nullptr;
};
```

### Шаг 4: Обнови PluginEditor

В `Source/PluginEditor.h`:

```cpp
#include "GUI/CustomLookAndFeel.h"

class LA2ACompressorEditor : public juce::AudioProcessorEditor
{
private:
    LA2ALookAndFeel customLookAndFeel;
    juce::Image backgroundImage;
    juce::Image needleImage;
    // ... остальное
};
```

В `Source/PluginEditor.cpp`:

```cpp
LA2ACompressorEditor::LA2ACompressorEditor(LA2ACompressorProcessor& p)
    : AudioProcessorEditor(&p), audioProcessor(p)
{
    // Загружаем фон
    backgroundImage = juce::ImageCache::getFromMemory(
        BinaryData::Background_png,
        BinaryData::Background_pngSize
    );

    // Применяем кастомный LookAndFeel
    customLookAndFeel.setSliders(&peakReductionSlider, &gainSlider);
    setLookAndFeel(&customLookAndFeel);

    // Настраиваем слайдеры (убираем стандартные элементы)
    peakReductionSlider.setTextBoxStyle(juce::Slider::NoTextBox, false, 0, 0);
    gainSlider.setTextBoxStyle(juce::Slider::NoTextBox, false, 0, 0);

    // ... остальное
}

void LA2ACompressorEditor::paint(juce::Graphics& g)
{
    // Рисуем фон
    if (backgroundImage.isValid())
    {
        g.drawImage(backgroundImage, getLocalBounds().toFloat());
    }

    // Рисуем стрелку VU-метра
    drawVUNeedle(g);
}

void LA2ACompressorEditor::drawVUNeedle(juce::Graphics& g)
{
    // Вычисляем угол стрелки на основе gainReductionMeterValue
    float angle = juce::jmap(gainReductionMeterValue, -20.0f, 0.0f, -45.0f, 45.0f);

    // Поворачиваем и рисуем стрелку
    juce::AffineTransform transform = juce::AffineTransform::rotation(
        angle * juce::MathConstants<float>::pi / 180.0f,
        needleCenterX, needleCenterY
    );

    g.drawImageTransformed(needleImage, transform);
}
```

## Подход 2: Полностью кастомная отрисовка

Если хочешь полный контроль:

### CustomKnob.h

```cpp
class CustomKnob : public juce::Component
{
public:
    CustomKnob(juce::AudioProcessorValueTreeState& apvts,
               const juce::String& paramID,
               const juce::Image& knobImage)
        : attachment(apvts, paramID, [this](float v) { setValue(v); })
        , image(knobImage)
    {
    }

    void paint(juce::Graphics& g) override
    {
        const int numFrames = 64;
        const int frameHeight = image.getHeight() / numFrames;
        const int frameIndex = (int)(value * (numFrames - 1));

        g.drawImage(image, getLocalBounds().toFloat(),
                   juce::RectanglePlacement::centred);
    }

    void mouseDown(const juce::MouseEvent& e) override
    {
        startDrag = e.y;
        startValue = value;
    }

    void mouseDrag(const juce::MouseEvent& e) override
    {
        float delta = (startDrag - e.y) / 100.0f;
        setValue(juce::jlimit(0.0f, 1.0f, startValue + delta));
    }

private:
    juce::ParameterAttachment attachment;
    juce::Image image;
    float value = 0.0f;
    float startDrag = 0.0f;
    float startValue = 0.0f;

    void setValue(float v)
    {
        value = v;
        repaint();
    }
};
```

## Координаты элементов

Для твоего дизайна определи координаты:

```cpp
// В PluginEditor.cpp resized()
void LA2ACompressorEditor::resized()
{
    // Координаты на основе твоего дизайна
    peakReductionSlider.setBounds(50, 100, 120, 120);
    gainSlider.setBounds(200, 100, 100, 100);
    limitModeButton.setBounds(350, 130, 100, 30);
    stereoLinkButton.setBounds(350, 170, 100, 30);

    // VU meter needle center
    needleCenterX = 250;
    needleCenterY = 300;
}
```

## Следующие шаги

1. **Создай дизайн** в графическом редакторе
2. **Экспортируй PNG** для каждого элемента
3. **Добавь в Resources/** папку
4. **Обнови CMakeLists.txt** для включения ресурсов
5. **Реализуй CustomLookAndFeel** или кастомные компоненты
6. **Настрой координаты** в resized()

## Советы

- Используй **высокое разрешение** (2x или 3x) для Retina дисплеев
- Создавай **filmstrip** анимации для плавного вращения ручек
- Тестируй на **разных размерах** окна
- Добавь **tooltips** для подсказок пользователю
- Рассмотри **масштабируемый UI** для разных DPI

## Пример структуры Resources/

```
Resources/
├── Background.png          # 500x400, основной фон
├── Knob_PeakReduction.png  # 100x6400, 64 кадра
├── Knob_Gain.png           # 80x5120, 64 кадра
├── Switch_Compress.png     # 50x30
├── Switch_Limit.png        # 50x30
├── LED_On.png              # 20x20
├── LED_Off.png             # 20x20
├── VUMeter_Needle.png      # 150x10
└── VUMeter_Scale.png       # 200x100, шкала метра
```

## Полезные ссылки

- JUCE ImageCache: https://docs.juce.com/master/classImageCache.html
- JUCE LookAndFeel: https://docs.juce.com/master/classLookAndFeel.html
- Filmstrip Tutorial: https://www.youtube.com/watch?v=example

Удачи с дизайном! 🎨
