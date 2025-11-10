#include "TransformerModel.h"
#include <cmath>

TransformerModel::TransformerModel()
{
}

void TransformerModel::prepare(double sr)
{
    sampleRate = sr;

    // Настраиваем фильтры для частотной характеристики трансформатора

    // Low shelf: небольшой подъем на ~100Hz для "теплоты"
    juce::dsp::ProcessSpec spec;
    spec.sampleRate = sampleRate;
    spec.maximumBlockSize = 1;
    spec.numChannels = 1;

    lowShelfFilter.prepare(spec);
    highCutFilter.prepare(spec);

    // Low shelf +1dB at 100Hz
    *lowShelfFilter.coefficients = *juce::dsp::IIR::Coefficients<float>::makeLowShelf(
        sampleRate, 100.0f, 0.7f, 1.12f); // +1dB

    // High cut -3dB at 15kHz (типичный roll-off трансформатора)
    *highCutFilter.coefficients = *juce::dsp::IIR::Coefficients<float>::makeLowPass(
        sampleRate, 15000.0f, 0.707f);

    reset();
}

void TransformerModel::reset()
{
    hysteresisState = 0.0f;
    lowShelfFilter.reset();
    highCutFilter.reset();
}

float TransformerModel::coreSaturation(float input, float saturationAmount)
{
    // Моделируем насыщение магнитного сердечника
    // Используем функцию, похожую на B-H кривую (кривая намагничивания)

    // Увеличиваем уровень для насыщения
    float driven = input * (1.0f + saturationAmount * 2.0f);

    // Arctangent saturation - создает как четные, так и нечетные гармоники
    float saturated = std::atan(driven * 1.5f) / std::atan(1.5f);

    // Добавляем легкую асимметрию для большего количества четных гармоник
    saturated = saturated + 0.05f * saturationAmount * saturated * saturated;

    return saturated;
}

float TransformerModel::hysteresisProcess(float input)
{
    // Упрощенная модель гистерезиса
    // Гистерезис вызывает "память" в магнитном сердечнике

    float hysteresisAmount = 0.15f;

    // Текущее состояние смешивается с входом
    hysteresisState = hysteresisAmount * hysteresisState + (1.0f - hysteresisAmount) * input;

    // Выход - комбинация текущего входа и состояния гистерезиса
    float output = 0.85f * input + 0.15f * hysteresisState;

    return output;
}

float TransformerModel::processSample(float input, float saturation)
{
    // 1. Моделируем гистерезис
    float withHysteresis = hysteresisProcess(input);

    // 2. Насыщение сердечника (генерирует гармоники)
    float saturated = coreSaturation(withHysteresis, saturation);

    // 3. Применяем частотную характеристику
    float withLowShelf = lowShelfFilter.processSample(saturated);
    float output = highCutFilter.processSample(withLowShelf);

    return output;
}
