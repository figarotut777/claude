#pragma once

#include <juce_audio_processors/juce_audio_processors.h>
#include <juce_gui_basics/juce_gui_basics.h>
#include "PluginProcessor.h"

/**
 * LA2ACompressorEditor - GUI плагина в стиле LA-2A
 *
 * Элементы управления:
 * - Peak Reduction (большая ручка)
 * - Gain (Make-up gain)
 * - Compress/Limit переключатель
 * - VU Meter для Gain Reduction
 */
class LA2ACompressorEditor : public juce::AudioProcessorEditor,
                              private juce::Timer
{
public:
    explicit LA2ACompressorEditor(LA2ACompressorProcessor&);
    ~LA2ACompressorEditor() override;

    void paint(juce::Graphics&) override;
    void resized() override;

private:
    void timerCallback() override;

    LA2ACompressorProcessor& audioProcessor;

    // Параметры
    juce::Slider peakReductionSlider;
    juce::Slider gainSlider;
    juce::ToggleButton limitModeButton;
    juce::ToggleButton stereoLinkButton;

    juce::Label peakReductionLabel;
    juce::Label gainLabel;
    juce::Label limitModeLabel;
    juce::Label stereoLinkLabel;
    juce::Label titleLabel;

    // Attachments для синхронизации с параметрами
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> peakReductionAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> gainAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::ButtonAttachment> limitModeAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::ButtonAttachment> stereoLinkAttachment;

    // Gain Reduction Meter
    float gainReductionMeterValue = 0.0f;

    void drawVUMeter(juce::Graphics& g, juce::Rectangle<int> bounds);

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(LA2ACompressorEditor)
};
