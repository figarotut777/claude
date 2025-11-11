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
        0.0f,
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
        false));

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
    }

    // Оверсэмплинг
    oversampler.prepare(spec);

    // Детекторы уровня
    levelDetectorL.prepare(spec);
    levelDetectorR.prepare(spec);
    levelDetectorL.setLevelCalculationType(juce::dsp::BallisticsFilterLevelCalculationType::RMS);
    levelDetectorR.setLevelCalculationType(juce::dsp::BallisticsFilterLevelCalculationType::RMS);
    levelDetectorL.setAttackTime(0.001f);  // 1ms
    levelDetectorL.setReleaseTime(0.1f);   // 100ms
    levelDetectorR.setAttackTime(0.001f);
    levelDetectorR.setReleaseTime(0.1f);
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

void LA2ACompressorProcessor::processChannel(int channel, float* channelData, int numSamples)
{
    auto& proc = channels[channel];

    // Получаем параметры
    float peakReduction = apvts.getRawParameterValue("peakReduction")->load() / 100.0f;
    bool limitMode = apvts.getRawParameterValue("limitMode")->load() > 0.5f;

    for (int i = 0; i < numSamples; ++i)
    {
        float sample = channelData[i];

        // 1. Входной трансформатор
        sample = proc.inputTransformer.processSample(sample, 0.3f);

        // 2. Входной ламповый каскад (легкое насыщение)
        sample = proc.inputTube.processSample(sample, 0.3f);

        // 3. Детектирование уровня для opto-cell
        float inputLevel = std::abs(sample);

        // 4. Opto-Cell компрессия
        float gainReduction = proc.optoCell.processSample(inputLevel, peakReduction, limitMode);

        // 5. Применяем компрессию
        sample *= gainReduction;

        // 6. Выходной ламповый каскад (добавляет гармоники)
        sample = proc.outputTube.processSample(sample, 0.4f);

        // 7. Выходной трансформатор
        sample = proc.outputTransformer.processSample(sample, 0.3f);

        channelData[i] = sample;

        // Обновляем gain reduction для GUI (только левый канал)
        if (channel == 0)
        {
            float grDB = juce::Decibels::gainToDecibels(gainReduction, -60.0f);
            currentGainReductionDB.store(grDB);
        }
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

    // Make-up Gain
    float makeupGainDB = apvts.getRawParameterValue("makeupGain")->load();
    float makeupGainLinear = juce::Decibels::decibelsToGain(makeupGainDB);

    // Оверсэмплинг + обработка
    juce::dsp::AudioBlock<float> block(buffer);

    oversampler.process(block, [&](juce::dsp::AudioBlock<float>& oversampledBlock)
    {
        // Обрабатываем каждый канал отдельно
        for (int channel = 0; channel < juce::jmin(2, (int)oversampledBlock.getNumChannels()); ++channel)
        {
            float* channelData = oversampledBlock.getChannelPointer(channel);
            int numSamples = (int)oversampledBlock.getNumSamples();
            processChannel(channel, channelData, numSamples);
        }
    });

    // Применяем Make-up Gain после оверсэмплинга
    for (int channel = 0; channel < totalNumInputChannels; ++channel)
    {
        auto* channelData = buffer.getWritePointer(channel);
        for (int i = 0; i < buffer.getNumSamples(); ++i)
        {
            channelData[i] *= makeupGainLinear;
            // Мягкое ограничение на выходе
            channelData[i] = juce::jlimit(-1.0f, 1.0f, channelData[i]);
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

// This creates the filter instance that the host calls
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    // Убедитесь, что имя класса здесь совпадает с именем вашего процессора
    return new LA2ACompressorAudioProcessor(); 
}
