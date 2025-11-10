#pragma once

#include <JuceHeader.h>

/**
 * TubeSaturation - Моделирует ламповое насыщение (Tube/Valve saturation)
 *
 * Особенности:
 * - Генерация четных гармоник (в основном 2-я)
 * - Мягкое ограничение (soft clipping)
 * - Асимметричное насыщение для реалистичности
 * - DC-фильтр для предотвращения DC offset
 */
class TubeSaturation
{
public:
    TubeSaturation();

    void prepare(double sampleRate);
    void reset();

    /**
     * Обрабатывает один сэмпл через ламповую секцию
     * @param input - входной сэмпл
     * @param drive - уровень драйва/насыщения (0-1)
     * @return обработанный сэмпл с гармониками
     */
    float processSample(float input, float drive = 0.5f);

private:
    double sampleRate = 44100.0;

    // DC blocker для удаления постоянной составляющей
    float dcBlockerX1 = 0.0f;
    float dcBlockerY1 = 0.0f;

    // Параметры лампы
    static constexpr float TUBE_BIAS = 0.1f;     // Смещение для асимметрии
    static constexpr float TUBE_WARMTH = 1.3f;   // Коэффициент "теплоты"

    // Ламповая передаточная характеристика (tanh с модификациями)
    float tubeTransferFunction(float input);

    // DC blocker
    float removeDC(float input);
};
