#include "PluginProcessor.h"
#include "PluginEditor.h"

//==============================================================================
LA2ACompressorEditor::LA2ACompressorEditor(LA2ACompressorProcessor& p)
    : AudioProcessorEditor(&p), audioProcessor(p)
{
    // Размер окна в стиле LA-2A
    setSize(500, 400);

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

    // VU Meter для Gain Reduction
    juce::Rectangle<int> meterBounds(getWidth() / 2 - 75, 280, 150, 80);
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

    bounds.removeFromTop(20); // Отступ

    // Верхний ряд с контролами
    auto controlsArea = bounds.removeFromTop(150);

    // Peak Reduction (левая большая ручка)
    auto peakReductionArea = controlsArea.removeFromLeft(150);
    peakReductionLabel.setBounds(peakReductionArea.removeFromTop(20));
    peakReductionSlider.setBounds(peakReductionArea);

    controlsArea.removeFromLeft(20); // Отступ

    // Gain (средняя ручка)
    auto gainArea = controlsArea.removeFromLeft(150);
    gainLabel.setBounds(gainArea.removeFromTop(20));
    gainSlider.setBounds(gainArea);

    controlsArea.removeFromLeft(20); // Отступ

    // Limit Mode (правый переключатель)
    auto limitArea = controlsArea;
    limitModeLabel.setBounds(limitArea.removeFromTop(20));
    limitModeButton.setBounds(limitArea.removeFromTop(30).reduced(10));

    // VU Meter рисуется в paint()
}

void LA2ACompressorEditor::timerCallback()
{
    // Обновляем значение gain reduction для VU meter
    float currentGR = audioProcessor.getCurrentGainReductionDB();

    // Сглаживание для плавного отображения
    float smoothing = 0.8f;
    gainReductionMeterValue = smoothing * gainReductionMeterValue + (1.0f - smoothing) * currentGR;

    repaint();
}
