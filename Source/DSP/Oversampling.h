#pragma once

#include <juce_dsp/juce_dsp.h>

/**
 * OversamplingProcessor - Обертка для 4x оверсэмплинга с использованием JUCE DSP
 *
 * Оверсэмплинг необходим для:
 * - Снижения алиасинга от нелинейных процессов (насыщение, компрессия)
 * - Улучшения качества моделирования аналоговых компонентов
 * - Более точной генерации гармоник
 */
template <typename SampleType>
class OversamplingProcessor
{
public:
    OversamplingProcessor()
        : oversampler(2, 2, juce::dsp::Oversampling<SampleType>::filterHalfBandPolyphaseIIR, true)
    {
        // 2 каналов, 2 stages = 4x oversampling
    }

    void prepare(const juce::dsp::ProcessSpec& spec)
    {
        oversampler.initProcessing(spec.maximumBlockSize);
    }

    void reset()
    {
        oversampler.reset();
    }

    /**
     * Процессит блок с оверсэмплингом
     * @param block - аудио блок для обработки
     * @param processFunction - функция обработки, которая будет вызвана для оверсэмплированного сигнала
     */
    template <typename ProcessFunction>
    void process(juce::dsp::AudioBlock<SampleType>& block, ProcessFunction&& processFunction)
    {
        // Апсэмплинг
        auto oversampledBlock = oversampler.processSamplesUp(block);

        // Обработка на повышенной частоте дискретизации
        processFunction(oversampledBlock);

        // Даунсэмплинг
        oversampler.processSamplesDown(block);
    }

    int getLatencySamples() const
    {
        return oversampler.getLatencyInSamples();
    }

private:
    juce::dsp::Oversampling<SampleType> oversampler;
};
