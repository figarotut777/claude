#include "PluginProcessor.h"
#include "PluginEditor.h"

//==============================================================================
LA2ACompressorEditor::LA2ACompressorEditor(LA2ACompressorProcessor& p)
    : AudioProcessorEditor(&p), audioProcessor(p)
{
    // Размер окна в стиле LA-2A
    setSize(600, 500);

    // Делаем окно изменяемого размера с ограничениями
    setResizable(true, true);
    setResizeLimits(500, 400, 1200, 1000); // min width, min height, max width, max height
    getConstrainer()->setFixedAspectRatio(1.2f); // Сохраняем пропорции 6:5

    // Title Label
    titleLabel.setText("LA-2A Optical Compressor", juce::dontSendNotification);
    titleLabel.setFont(juce::Font(24.0f, juce::Font::bold));
    titleLabel.setJustificationType(juce::Justification::centred);
    titleLabel.setColour(juce::Label::textColourId, juce::Colours::silver);
    addAndMakeVisible(titleLabel);

    // Peak Reduction Slider (большая круглая ручка)
    peakReductionSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
    peakReductionSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    peakReductionSlider.setColour(juce::Slider::thumbColourId, juce::Colours::silver);
    peakReductionSlider.setColour(juce::Slider::rotarySliderFillColourId, juce::Colours::lightblue);
    addAndMakeVisible(peakReductionSlider);

    peakReductionLabel.setText("Peak Reduction", juce::dontSendNotification);
    peakReductionLabel.setJustificationType(juce::Justification::centred);
    peakReductionLabel.setColour(juce::Label::textColourId, juce::Colours::silver);
    addAndMakeVisible(peakReductionLabel);

    peakReductionAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment>(
        audioProcessor.getValueTreeState(), "peakReduction", peakReductionSlider);

    // Gain Slider
    gainSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
    gainSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    gainSlider.setColour(juce::Slider::thumbColourId, juce::Colours::silver);
    gainSlider.setColour(juce::Slider::rotarySliderFillColourId, juce::Colours::lightgreen);
    addAndMakeVisible(gainSlider);

    gainLabel.setText("Gain", juce::dontSendNotification);
    gainLabel.setJustificationType(juce::Justification::centred);
    gainLabel.setColour(juce::Label::textColourId, juce::Colours::silver);
    addAndMakeVisible(gainLabel);

    gainAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment>(
        audioProcessor.getValueTreeState(), "makeupGain", gainSlider);

    // Limit Mode Button
    limitModeButton.setButtonText("Limit");
    limitModeButton.setColour(juce::ToggleButton::textColourId, juce::Colours::silver);
    limitModeButton.setColour(juce::ToggleButton::tickColourId, juce::Colours::red);
    addAndMakeVisible(limitModeButton);

    limitModeLabel.setText("Compress / Limit", juce::dontSendNotification);
    limitModeLabel.setJustificationType(juce::Justification::centred);
    limitModeLabel.setColour(juce::Label::textColourId, juce::Colours::silver);
    addAndMakeVisible(limitModeLabel);

    limitModeAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ButtonAttachment>(
        audioProcessor.getValueTreeState(), "limitMode", limitModeButton);

    // Stereo Link Button
    stereoLinkButton.setButtonText("Stereo Link");
    stereoLinkButton.setColour(juce::ToggleButton::textColourId, juce::Colours::silver);
    stereoLinkButton.setColour(juce::ToggleButton::tickColourId, juce::Colours::green);
    addAndMakeVisible(stereoLinkButton);

    stereoLinkLabel.setText("Stereo Link", juce::dontSendNotification);
    stereoLinkLabel.setJustificationType(juce::Justification::centred);
    stereoLinkLabel.setColour(juce::Label::textColourId, juce::Colours::silver);
    addAndMakeVisible(stereoLinkLabel);

    stereoLinkAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ButtonAttachment>(
        audioProcessor.getValueTreeState(), "stereoLink", stereoLinkButton);

    // HPF Frequency Slider
    hpfFreqSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
    hpfFreqSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    hpfFreqSlider.setColour(juce::Slider::thumbColourId, juce::Colours::silver);
    hpfFreqSlider.setColour(juce::Slider::rotarySliderFillColourId, juce::Colours::orange);
    addAndMakeVisible(hpfFreqSlider);

    hpfFreqLabel.setText("HPF", juce::dontSendNotification);
    hpfFreqLabel.setJustificationType(juce::Justification::centred);
    hpfFreqLabel.setColour(juce::Label::textColourId, juce::Colours::silver);
    addAndMakeVisible(hpfFreqLabel);

    hpfFreqAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment>(
        audioProcessor.getValueTreeState(), "hpfFreq", hpfFreqSlider);

    // Mix Slider
    mixSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
    mixSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    mixSlider.setColour(juce::Slider::thumbColourId, juce::Colours::silver);
    mixSlider.setColour(juce::Slider::rotarySliderFillColourId, juce::Colours::cyan);
    addAndMakeVisible(mixSlider);

    mixLabel.setText("Mix", juce::dontSendNotification);
    mixLabel.setJustificationType(juce::Justification::centred);
    mixLabel.setColour(juce::Label::textColourId, juce::Colours::silver);
    addAndMakeVisible(mixLabel);

    mixAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment>(
        audioProcessor.getValueTreeState(), "mix", mixSlider);

    // Auto Gain Button
    autoGainButton.setButtonText("Auto Gain");
    autoGainButton.setColour(juce::ToggleButton::textColourId, juce::Colours::silver);
    autoGainButton.setColour(juce::ToggleButton::tickColourId, juce::Colours::yellow);
    addAndMakeVisible(autoGainButton);

    autoGainLabel.setText("Auto Gain", juce::dontSendNotification);
    autoGainLabel.setJustificationType(juce::Justification::centred);
    autoGainLabel.setColour(juce::Label::textColourId, juce::Colours::silver);
    addAndMakeVisible(autoGainLabel);

    autoGainAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ButtonAttachment>(
        audioProcessor.getValueTreeState(), "autoGain", autoGainButton);

    // Power Button
    powerButton.setButtonText("POWER");
    powerButton.setColour(juce::ToggleButton::textColourId, juce::Colours::silver);
    powerButton.setColour(juce::ToggleButton::tickColourId, juce::Colours::lime);
    addAndMakeVisible(powerButton);

    powerLabel.setText("Power", juce::dontSendNotification);
    powerLabel.setJustificationType(juce::Justification::centred);
    powerLabel.setColour(juce::Label::textColourId, juce::Colours::silver);
    addAndMakeVisible(powerLabel);

    powerAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ButtonAttachment>(
        audioProcessor.getValueTreeState(), "power", powerButton);

    // Запускаем таймер для обновления VU meter
    startTimerHz(30); // 30 fps
}

LA2ACompressorEditor::~LA2ACompressorEditor()
{
}

//==============================================================================
void LA2ACompressorEditor::paint(juce::Graphics& g)
{
    // Фон в стиле винтажного оборудования
    g.fillAll(juce::Colour(0xff2a2a2a));

    // Панель в стиле металла
    juce::Rectangle<int> panel = getLocalBounds().reduced(10);
    g.setColour(juce::Colour(0xff3a3a3a));
    g.fillRoundedRectangle(panel.toFloat(), 10.0f);

    // Рамка
    g.setColour(juce::Colours::silver);
    g.drawRoundedRectangle(panel.toFloat(), 10.0f, 2.0f);

    // VU Meter для Gain Reduction (в центре между GAIN и PEAK REDUCTION)
    // Позиция соответствует centerSection из resized()
    int centerX = 150 + 10; // leftSection + отступ
    int centerY = 50 + 10; // title + отступ
    int centerWidth = 200;
    int centerHeight = 200;

    juce::Rectangle<int> meterBounds(centerX + 25, centerY + 40, 150, 120);
    drawVUMeter(g, meterBounds);
}

void LA2ACompressorEditor::drawVUMeter(juce::Graphics& g, juce::Rectangle<int> bounds)
{
    // Фон метра
    g.setColour(juce::Colour(0xff1a1a1a));
    g.fillRoundedRectangle(bounds.toFloat(), 5.0f);

    // Рамка
    g.setColour(juce::Colours::silver);
    g.drawRoundedRectangle(bounds.toFloat(), 5.0f, 1.0f);

    // Label
    g.setColour(juce::Colours::silver);
    g.setFont(12.0f);
    g.drawText("Gain Reduction", bounds.getX(), bounds.getY() + 5,
               bounds.getWidth(), 15, juce::Justification::centred);

    // Meter bar
    juce::Rectangle<int> barBounds = bounds.reduced(10, 25);
    barBounds.removeFromTop(10);

    // Background bar
    g.setColour(juce::Colour(0xff3a3a3a));
    g.fillRect(barBounds);

    // Значение в dB (от 0 до -20 dB)
    float grDB = gainReductionMeterValue;
    float normalizedValue = juce::jmap(grDB, -20.0f, 0.0f, 0.0f, 1.0f);
    normalizedValue = juce::jlimit(0.0f, 1.0f, normalizedValue);

    // Meter fill
    int fillWidth = static_cast<int>(barBounds.getWidth() * normalizedValue);
    juce::Rectangle<int> fillRect = barBounds.withWidth(fillWidth);

    // Gradient от зеленого к красному
    juce::ColourGradient gradient(
        juce::Colours::green, fillRect.getX(), fillRect.getY(),
        juce::Colours::red, fillRect.getRight(), fillRect.getY(), false);

    g.setGradientFill(gradient);
    g.fillRect(fillRect);

    // Значение текстом
    g.setColour(juce::Colours::silver);
    juce::String valueText = juce::String(grDB, 1) + " dB";
    g.drawText(valueText, barBounds.getX(), barBounds.getBottom() + 5,
               barBounds.getWidth(), 20, juce::Justification::centred);
}

void LA2ACompressorEditor::resized()
{
    auto bounds = getLocalBounds().reduced(20);

    // Title
    titleLabel.setBounds(bounds.removeFromTop(50));

    bounds.removeFromTop(10); // Отступ

    // Основной ряд (LA-2A стиль): Limit/Compress - GAIN - VU Meter - PEAK REDUCTION - POWER
    auto mainRow = bounds.removeFromTop(200);

    // Левая часть: Limit/Compress toggle + GAIN knob
    auto leftSection = mainRow.removeFromLeft(150);

    // Limit/Compress toggle слева от GAIN
    limitModeLabel.setBounds(leftSection.removeFromTop(20));
    limitModeButton.setBounds(leftSection.removeFromTop(40).reduced(15, 5));

    leftSection.removeFromTop(10); // Отступ

    // GAIN knob
    gainLabel.setBounds(leftSection.removeFromTop(20));
    gainSlider.setBounds(leftSection);

    mainRow.removeFromLeft(10); // Отступ

    // Центр: VU Meter (рисуется в paint, резервируем место)
    auto centerSection = mainRow.removeFromLeft(200);
    // VU Meter будет отрисован в центре через paint()

    mainRow.removeFromLeft(10); // Отступ

    // Правая часть: PEAK REDUCTION knob + POWER toggle
    auto rightSection = mainRow;

    // PEAK REDUCTION knob
    peakReductionLabel.setBounds(rightSection.removeFromTop(20));
    peakReductionSlider.setBounds(rightSection.removeFromBottom(130));

    rightSection.removeFromTop(10); // Отступ

    // POWER toggle справа от PEAK REDUCTION
    powerLabel.setBounds(rightSection.removeFromTop(20));
    powerButton.setBounds(rightSection.removeFromTop(40).reduced(15, 5));

    bounds.removeFromTop(20); // Отступ

    // Нижний ряд: HPF, Mix, Auto Gain, Stereo Link
    auto bottomRow = bounds.removeFromTop(120);

    // HPF
    auto hpfArea = bottomRow.removeFromLeft(120);
    hpfFreqLabel.setBounds(hpfArea.removeFromTop(20));
    hpfFreqSlider.setBounds(hpfArea);

    bottomRow.removeFromLeft(10); // Отступ

    // Mix
    auto mixArea = bottomRow.removeFromLeft(120);
    mixLabel.setBounds(mixArea.removeFromTop(20));
    mixSlider.setBounds(mixArea);

    bottomRow.removeFromLeft(10); // Отступ

    // Auto Gain toggle
    auto autoGainArea = bottomRow.removeFromLeft(120);
    autoGainLabel.setBounds(autoGainArea.removeFromTop(20));
    autoGainButton.setBounds(autoGainArea.removeFromTop(40).reduced(15, 5));

    bottomRow.removeFromLeft(10); // Отступ

    // Stereo Link toggle
    auto stereoLinkArea = bottomRow;
    stereoLinkLabel.setBounds(stereoLinkArea.removeFromTop(20));
    stereoLinkButton.setBounds(stereoLinkArea.removeFromTop(40).reduced(15, 5));
}

void LA2ACompressorEditor::timerCallback()
{
    // Обновляем значение gain reduction для VU meter
    float currentGR = audioProcessor.getCurrentGainReductionDB();

    // VU meter ballistics: быстрый attack, медленный release (как настоящий VU-метр)
    // Attack: ~300ms, Release: ~300ms для VU, но для GR meter делаем чуть быстрее
    float attackCoeff = 0.85f;  // Быстрая реакция на увеличение компрессии
    float releaseCoeff = 0.92f; // Медленный возврат (инерция)

    // Если компрессия усиливается (GR становится более отрицательным), используем attack
    // Если компрессия ослабевает (GR идет к 0), используем release
    if (currentGR < gainReductionMeterValue)
    {
        // Attack - быстрое движение вниз (больше компрессии)
        gainReductionMeterValue = attackCoeff * gainReductionMeterValue + (1.0f - attackCoeff) * currentGR;
    }
    else
    {
        // Release - медленное движение вверх (меньше компрессии) с инерцией
        gainReductionMeterValue = releaseCoeff * gainReductionMeterValue + (1.0f - releaseCoeff) * currentGR;
    }

    repaint();
}
