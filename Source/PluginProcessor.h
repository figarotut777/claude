#pragma once

#include <juce_audio_processors/juce_audio_processors.h>
#include <juce_dsp/juce_dsp.h>
#include "DSP/OptoCell.h"
#include "DSP/TubeSaturation.h"
#include "DSP/TransformerModel.h"
#include "DSP/Oversampling.h"

/**
 * LA2ACompressorProcessor - Главный процессор плагина
 *
 * Сигнальная цепь:
 * Input -> Input Transformer -> Tube Saturation -> Opto-Cell Compression ->
 * Output Transformer -> Make-up Gain -> Output
 *
 * С 4x оверсэмплингом для всех нелинейных процессов
 */
class LA2ACompressorProcessor : public juce::AudioProcessor
{
public:
    LA2ACompressorProcessor();
    ~LA2ACompressorProcessor() override;

    void prepareToPlay(double sampleRate, int samplesPerBlock) override;
    void releaseResources() override;

    bool isBusesLayoutSupported(const BusesLayout& layouts) const override;

    void processBlock(juce::AudioBuffer<float>&, juce::MidiBuffer&) override;

    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override;

    const juce::String getName() const override;

    bool acceptsMidi() const override;
    bool producesMidi() const override;
    bool isMidiEffect() const override;
    double getTailLengthSeconds() const override;

    int getNumPrograms() override;
    int getCurrentProgram() override;
    void setCurrentProgram(int index) override;
    const juce::String getProgramName(int index) override;
    void changeProgramName(int index, const juce::String& newName) override;

    void getStateInformation(juce::MemoryBlock& destData) override;
    void setStateInformation(const void* data, int sizeInBytes) override;

    // Параметры
    juce::AudioProcessorValueTreeState& getValueTreeState() { return apvts; }

    // Для GUI - текущий gain reduction в dB
    float getCurrentGainReductionDB() const { return currentGainReductionDB.load(); }

private:
    // AudioProcessorValueTreeState для управления параметрами
    juce::AudioProcessorValueTreeState apvts;

    static juce::AudioProcessorValueTreeState::ParameterLayout createParameterLayout();

    // DSP компоненты для стерео (L/R каналы)
    struct ChannelProcessor
    {
        OptoCell optoCell;
        TubeSaturation inputTube;
        TubeSaturation outputTube;
        TransformerModel inputTransformer;
        TransformerModel outputTransformer;
    };

    std::array<ChannelProcessor, 2> channels; // L/R

    // Оверсэмплинг
    OversamplingProcessor<float> oversampler;

    // Детектор уровня (RMS/Peak)
    juce::dsp::BallisticsFilter<float> levelDetectorL;
    juce::dsp::BallisticsFilter<float> levelDetectorR;

    // Gain Reduction для GUI
    std::atomic<float> currentGainReductionDB { 0.0f };

    // Обработка одного канала
    void processChannel(int channel, float* channelData, int numSamples);

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(LA2ACompressorProcessor)
};
