#pragma once

#include <JuceHeader.h>

/**
 * TransformerModel - Моделирует входной и выходной трансформаторы
 *
 * Особенности:
 * - Генерация 2-й и 3-й гармоник через насыщение сердечника
 * - Моделирование гистерезиса
 * - Симуляция частотной характеристики трансформатора
 * - Low-frequency bump и high-frequency roll-off
 */
class TransformerModel
{
public:
    TransformerModel();

    void prepare(double sampleRate);
    void reset();

    /**
     * Обрабатывает сигнал через модель трансформатора
     * @param input - входной сэмпл
     * @param saturation - уровень насыщения сердечника (0-1)
     * @return обработанный сэмпл
     */
    float processSample(float input, float saturation = 0.3f);

private:
    double sampleRate = 44100.0;

    // Состояние гистерезиса
    float hysteresisState = 0.0f;

    // Фильтры для моделирования частотной характеристики
    juce::dsp::IIR::Filter<float> lowShelfFilter;   // Bump на низких частотах
    juce::dsp::IIR::Filter<float> highCutFilter;    // Roll-off на высоких

    // Моделирование насыщения сердечника (генерирует гармоники)
    float coreSaturation(float input, float saturationAmount);

    // Простая модель гистерезиса
    float hysteresisProcess(float input);
};
