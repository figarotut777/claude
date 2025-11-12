#include "PluginProcessor.h"
#include "PluginEditor.h"

//==============================================================================
LA2ACompressorProcessor::LA2ACompressorProcessor()
    : AudioProcessor(BusesProperties()
                         .withInput("Input", juce::AudioChannelSet::stereo(), true)
                         .withOutput("Output", juce::AudioChannelSet::stereo(), true)),
      apvts(*this, nullptr, "PARAMETERS", createParameterLayout())
{
}

LA2ACompressorProcessor::~LA2ACompressorProcessor()
{
}

//==============================================================================
juce::AudioProcessorValueTreeState::ParameterLayout LA2ACompressorProcessor::createParameterLayout()
{
    juce::AudioProcessorValueTreeState::ParameterLayout layout;

    // Peak Reduction (0-100%)
    layout.add(std::make_unique<juce::AudioParameterFloat>(
        "peakReduction",
        "Peak Reduction",
        juce::NormalisableRange<float>(0.0f, 100.0f, 0.1f),
        30.0f,  // Default 30% - умеренная компрессия
        "%"));

    // Make-up Gain (-20 to +20 dB)
    layout.add(std::make_unique<juce::AudioParameterFloat>(
        "makeupGain",
        "Gain",
        juce::NormalisableRange<float>(-20.0f, 20.0f, 0.1f),
        0.0f,
        "dB"));

    // Compress/Limit switch (false = Compress, true = Limit)
    layout.add(std::make_unique<juce::AudioParameterBool>(
        "limitMode",
        "Limit Mode",
        false));  // Default Compress

    // Stereo Link (true = linked, false = independent)
    layout.add(std::make_unique<juce::AudioParameterBool>(
        "stereoLink",
        "Stereo Link",
        true));  // Default ON

    // High Pass Filter frequency (20Hz - 500Hz)
    layout.add(std::make_unique<juce::AudioParameterFloat>(
        "hpfFreq",
        "HPF Frequency",
        juce::NormalisableRange<float>(20.0f, 500.0f, 1.0f, 0.3f),
        20.0f,  // Default 20Hz (почти выключен)
        "Hz"));

    // Mix (Dry/Wet) 0-100%
    layout.add(std::make_unique<juce::AudioParameterFloat>(
        "mix",
        "Mix",
        juce::NormalisableRange<float>(0.0f, 100.0f, 0.1f),
        100.0f,  // Default 100% wet
        "%"));

    // Auto Gain (automatic makeup)
    layout.add(std::make_unique<juce::AudioParameterBool>(
        "autoGain",
        "Auto Gain",
        false));  // Default OFF

    // Power On/Off
    layout.add(std::make_unique<juce::AudioParameterBool>(
        "power",
        "Power",
        true));  // Default ON

    return layout;
}

//==============================================================================
const juce::String LA2ACompressorProcessor::getName() const
{
    return JucePlugin_Name;
}

bool LA2ACompressorProcessor::acceptsMidi() const { return false; }
bool LA2ACompressorProcessor::producesMidi() const { return false; }
bool LA2ACompressorProcessor::isMidiEffect() const { return false; }
double LA2ACompressorProcessor::getTailLengthSeconds() const { return 0.0; }

int LA2ACompressorProcessor::getNumPrograms() { return 1; }
int LA2ACompressorProcessor::getCurrentProgram() { return 0; }
void LA2ACompressorProcessor::setCurrentProgram(int) {}
const juce::String LA2ACompressorProcessor::getProgramName(int) { return {}; }
void LA2ACompressorProcessor::changeProgramName(int, const juce::String&) {}

//==============================================================================
void LA2ACompressorProcessor::prepareToPlay(double sampleRate, int samplesPerBlock)
{
    juce::dsp::ProcessSpec spec;
    spec.sampleRate = sampleRate;
    spec.maximumBlockSize = static_cast<juce::uint32>(samplesPerBlock);
    spec.numChannels = 2;

    // Подготовка DSP компонентов для каждого канала
    for (auto& channel : channels)
    {
        channel.optoCell.prepare(sampleRate);
        channel.inputTube.prepare(sampleRate);
        channel.outputTube.prepare(sampleRate);
        channel.inputTransformer.prepare(sampleRate);
        channel.outputTransformer.prepare(sampleRate);

        // HPF filter initialization
        channel.hpFilter.prepare(spec);
        channel.hpFilter.reset();
    }

    // Оверсэмплинг
    oversampler.prepare(spec);
}

void LA2ACompressorProcessor::releaseResources()
{
    oversampler.reset();
}

bool LA2ACompressorProcessor::isBusesLayoutSupported(const BusesLayout& layouts) const
{
    if (layouts.getMainOutputChannelSet() != juce::AudioChannelSet::stereo())
        return false;

    if (layouts.getMainInputChannelSet() != layouts.getMainOutputChannelSet())
        return false;

    return true;
}

float LA2ACompressorProcessor::calculateRMS(const float* channelData, int numSamples)
{
    float sum = 0.0f;
    for (int i = 0; i < numSamples; ++i)
    {
        float sample = channelData[i];
        sum += sample * sample;
    }
    return std::sqrt(sum / numSamples);
}

void LA2ACompressorProcessor::processChannel(int channel, float* channelData, int numSamples,
                                            float peakReduction, bool limitMode, bool stereoLink,
                                            float hpfFreq, bool power)
{
    auto& proc = channels[channel];

    // Если power выключен - bypass
    if (!power)
    {
        return;
    }

    // 1. Применяем входной трансформатор и лампу (УМЕНЬШЕННОЕ насыщение)
    for (int i = 0; i < numSamples; ++i)
    {
        float sample = channelData[i];

        // Входной трансформатор (уменьшено с 0.3 до 0.1)
        sample = proc.inputTransformer.processSample(sample, 0.1f);

        // Входной ламповый каскад (уменьшено с 0.3 до 0.15)
        sample = proc.inputTube.processSample(sample, 0.15f);

        channelData[i] = sample;
    }

    // 2. High-pass filter для sidechain detection
    // Обновляем коэффициенты HPF если частота изменилась
    *proc.hpFilter.coefficients = *juce::dsp::IIR::Coefficients<float>::makeHighPass(
        getSampleRate() * 4.0, hpfFreq); // 4x для оверсэмплинга

    // Фильтруем копию сигнала для детекции
    float filteredData[numSamples];
    for (int i = 0; i < numSamples; ++i)
    {
        filteredData[i] = proc.hpFilter.processSample(channelData[i]);
    }

    // 3. Детектируем уровень (RMS с сглаживанием) на отфильтрованном сигнале
    float currentRMS = calculateRMS(filteredData, numSamples);

    // Сглаживаем RMS для более плавной работы компрессора
    float rmsSmoothing = 0.3f; // Больше = медленнее
    proc.rmsLevelState = rmsSmoothing * proc.rmsLevelState + (1.0f - rmsSmoothing) * currentRMS;

    // Используем сглаженный уровень для компрессии
    float detectionLevel = proc.rmsLevelState;

    // Для Stereo Link используем максимальный уровень из обоих каналов
    if (stereoLink)
    {
        detectionLevel = linkedLevel;
    }

    // 4. Применяем компрессию через Opto-Cell
    float gainReduction = 1.0f;

    for (int i = 0; i < numSamples; ++i)
    {
        // Opto-Cell обрабатывает детектированный уровень
        gainReduction = proc.optoCell.processSample(detectionLevel, peakReduction, limitMode);

        // Применяем компрессию к сигналу (НЕ к отфильтрованному!)
        float sample = channelData[i] * gainReduction;

        // Выходной ламповый каскад (уменьшено с 0.4 до 0.2)
        sample = proc.outputTube.processSample(sample, 0.2f);

        // Выходной трансформатор (уменьшено с 0.3 до 0.1)
        sample = proc.outputTransformer.processSample(sample, 0.1f);

        channelData[i] = sample;
    }

    // Обновляем gain reduction для GUI (только левый канал)
    if (channel == 0)
    {
        float grDB = juce::Decibels::gainToDecibels(gainReduction, -60.0f);
        currentGainReductionDB.store(grDB);
    }
}

void LA2ACompressorProcessor::updateAutoGain(float inputRMS, float outputRMS)
{
    // Простое вычисление auto gain: компенсируем разницу между входом и выходом
    if (inputRMS > 0.001f && outputRMS > 0.001f)
    {
        float gainDiff = inputRMS / outputRMS;
        float gainDiffDB = juce::Decibels::gainToDecibels(gainDiff);

        // Сглаживание
        float smoothing = 0.95f;
        autoGainCompensation = smoothing * autoGainCompensation + (1.0f - smoothing) * gainDiffDB;

        // Ограничиваем до разумных пределов
        autoGainCompensation = juce::jlimit(-20.0f, 20.0f, autoGainCompensation);
    }
}

void LA2ACompressorProcessor::processBlock(juce::AudioBuffer<float>& buffer,
                                            juce::MidiBuffer&)
{
    juce::ScopedNoDenormals noDenormals;

    auto totalNumInputChannels = getTotalNumInputChannels();
    auto totalNumOutputChannels = getTotalNumOutputChannels();

    // Очищаем лишние выходные каналы
    for (auto i = totalNumInputChannels; i < totalNumOutputChannels; ++i)
        buffer.clear(i, 0, buffer.getNumSamples());

    // Получаем параметры
    float peakReduction = apvts.getRawParameterValue("peakReduction")->load() / 100.0f;
    bool limitMode = apvts.getRawParameterValue("limitMode")->load() > 0.5f;
    bool stereoLink = apvts.getRawParameterValue("stereoLink")->load() > 0.5f;
    float hpfFreq = apvts.getRawParameterValue("hpfFreq")->load();
    float mix = apvts.getRawParameterValue("mix")->load() / 100.0f;
    bool autoGain = apvts.getRawParameterValue("autoGain")->load() > 0.5f;
    bool power = apvts.getRawParameterValue("power")->load() > 0.5f;
    float makeupGainDB = apvts.getRawParameterValue("makeupGain")->load();

    // Если power выключен - bypass
    if (!power)
    {
        return;
    }

    // Сохраняем dry сигнал для mix
    juce::AudioBuffer<float> dryBuffer;
    dryBuffer.makeCopyOf(buffer);

    // Вычисляем input RMS для auto gain
    float inputRMS = 0.0f;
    if (autoGain)
    {
        for (int ch = 0; ch < totalNumInputChannels; ++ch)
        {
            inputRMS += calculateRMS(buffer.getReadPointer(ch), buffer.getNumSamples());
        }
        inputRMS /= totalNumInputChannels;
    }

    // Оверсэмплинг + обработка
    juce::dsp::AudioBlock<float> block(buffer);

    oversampler.process(block, [&](juce::dsp::AudioBlock<float>& oversampledBlock)
    {
        int numChannels = juce::jmin(2, (int)oversampledBlock.getNumChannels());
        int numSamples = (int)oversampledBlock.getNumSamples();

        // Для Stereo Link: вычисляем максимальный RMS из обоих каналов
        if (stereoLink && numChannels == 2)
        {
            float rmsL = calculateRMS(oversampledBlock.getChannelPointer(0), numSamples);
            float rmsR = calculateRMS(oversampledBlock.getChannelPointer(1), numSamples);

            // Используем максимум для Stereo Link
            linkedLevel = std::max(rmsL, rmsR);
        }

        // Обрабатываем каждый канал
        for (int channel = 0; channel < numChannels; ++channel)
        {
            float* channelData = oversampledBlock.getChannelPointer(channel);
            processChannel(channel, channelData, numSamples,
                         peakReduction, limitMode, stereoLink, hpfFreq, true);
        }
    });

    // Вычисляем output RMS для auto gain
    float outputRMS = 0.0f;
    if (autoGain)
    {
        for (int ch = 0; ch < totalNumInputChannels; ++ch)
        {
            outputRMS += calculateRMS(buffer.getReadPointer(ch), buffer.getNumSamples());
        }
        outputRMS /= totalNumInputChannels;

        updateAutoGain(inputRMS, outputRMS);
        makeupGainDB += autoGainCompensation;
    }

    // Применяем Make-up Gain
    float makeupGainLinear = juce::Decibels::decibelsToGain(makeupGainDB);

    // Mix dry/wet и применяем gain
    for (int channel = 0; channel < totalNumInputChannels; ++channel)
    {
        auto* wetData = buffer.getWritePointer(channel);
        const auto* dryData = dryBuffer.getReadPointer(channel);

        for (int i = 0; i < buffer.getNumSamples(); ++i)
        {
            // Mix
            float wetSample = wetData[i] * makeupGainLinear;
            float drySample = dryData[i];
            float mixed = wetSample * mix + drySample * (1.0f - mix);

            // Мягкое ограничение на выходе
            wetData[i] = juce::jlimit(-1.0f, 1.0f, mixed);
        }
    }
}

//==============================================================================
bool LA2ACompressorProcessor::hasEditor() const
{
    return true;
}

juce::AudioProcessorEditor* LA2ACompressorProcessor::createEditor()
{
    return new LA2ACompressorEditor(*this);
}

//==============================================================================
void LA2ACompressorProcessor::getStateInformation(juce::MemoryBlock& destData)
{
    auto state = apvts.copyState();
    std::unique_ptr<juce::XmlElement> xml(state.createXml());
    copyXmlToBinary(*xml, destData);
}

void LA2ACompressorProcessor::setStateInformation(const void* data, int sizeInBytes)
{
    std::unique_ptr<juce::XmlElement> xmlState(getXmlFromBinary(data, sizeInBytes));

    if (xmlState.get() != nullptr)
        if (xmlState->hasTagName(apvts.state.getType()))
            apvts.replaceState(juce::ValueTree::fromXml(*xmlState));
}

//==============================================================================
// This creates new instances of the plugin..
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new LA2ACompressorProcessor();
}
