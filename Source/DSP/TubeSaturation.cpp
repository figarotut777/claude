#include "TubeSaturation.h"
#include <cmath>

TubeSaturation::TubeSaturation()
{
}

void TubeSaturation::prepare(double sr)
{
    sampleRate = sr;
    reset();
}

void TubeSaturation::reset()
{
    dcBlockerX1 = 0.0f;
    dcBlockerY1 = 0.0f;
}

float TubeSaturation::tubeTransferFunction(float input)
{
    // Моделируем характеристику триода (12AX7/ECC83)
    // Используем модифицированный tanh для создания гармоник

    // Добавляем асимметрию (bias) для генерации четных гармоник
    float biasedInput = input + TUBE_BIAS * input * input;

    // Основная передаточная характеристика (soft clipping)
    // tanh создает нечетные гармоники, но асимметрия добавляет четные
    float output = std::tanh(biasedInput * TUBE_WARMTH);

    // Добавляем легкую кубическую нелинейность для 3-й гармоники
    output = output + 0.05f * output * output * output;

    return output;
}

float TubeSaturation::removeDC(float input)
{
    // DC blocking filter (high-pass filter at ~5 Hz)
    // y[n] = x[n] - x[n-1] + 0.995 * y[n-1]
    float dcBlockerCoeff = 0.995f;

    float output = input - dcBlockerX1 + dcBlockerCoeff * dcBlockerY1;

    dcBlockerX1 = input;
    dcBlockerY1 = output;

    return output;
}

float TubeSaturation::processSample(float input, float drive)
{
    // 1. Применяем drive (усиление перед насыщением)
    // drive: 0 = чистый сигнал, 1 = максимальное насыщение
    float driveAmount = 1.0f + drive * 4.0f; // 1x - 5x усиление
    float driven = input * driveAmount;

    // 2. Ламповая передаточная функция
    float saturated = tubeTransferFunction(driven);

    // 3. Компенсируем усиление
    float output = saturated / driveAmount;

    // 4. Удаляем DC offset
    output = removeDC(output);

    // 5. Мягкое ограничение на выходе для безопасности
    output = juce::jlimit(-1.0f, 1.0f, output);

    return output;
}
