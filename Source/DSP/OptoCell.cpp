#include "OptoCell.h"
#include <cmath>

OptoCell::OptoCell()
{
}

void OptoCell::prepare(double sr)
{
    sampleRate = sr;
    reset();
}

void OptoCell::reset()
{
    optoCellState = 0.0f;
    currentGainReduction = 1.0f;
    fastReleaseState = 0.0f;
    slowReleaseState = 0.0f;
}

float OptoCell::calculateTimeConstant(float timeInSeconds)
{
    // Exponential smoothing coefficient
    return std::exp(-1.0f / (timeInSeconds * static_cast<float>(sampleRate)));
}

float OptoCell::calculateAttackTime(float inputLevel)
{
    // Нелинейное время attack: чем выше уровень, тем быстрее attack
    // Используем экспоненциальную зависимость
    float normalizedLevel = juce::jlimit(0.0f, 1.0f, inputLevel);

    // При низких уровнях - медленный attack, при высоких - быстрый
    float attackTime = MIN_ATTACK_TIME + (MAX_ATTACK_TIME - MIN_ATTACK_TIME) *
                       std::exp(-5.0f * normalizedLevel);

    return attackTime;
}

float OptoCell::processSample(float inputLevel, float peakReduction, bool isLimitMode)
{
    // 1. Вычисляем целевой уровень компрессии
    // Peak Reduction работает как threshold: 0 = высокий порог (мало компрессии),
    // 1 = низкий порог (много компрессии)

    // Threshold диапазон: от 0.001 (-60dB) до 1.0 (0dB)
    // При peakReduction=0: threshold=1.0 (не срабатывает)
    // При peakReduction=1.0: threshold=0.001 (срабатывает почти всегда)
    float threshold = std::exp(-peakReduction * 6.9f); // e^(-6.9) ≈ 0.001
    threshold = juce::jlimit(0.001f, 1.0f, threshold);

    // Определяем ratio на основе режима
    float ratio = isLimitMode ? 20.0f : 3.0f; // Limit ≈ 20:1, Compress ≈ 3:1

    // Вычисляем насколько нужно подавить сигнал
    float targetGain = 1.0f;

    if (inputLevel > threshold && inputLevel > 0.0001f)
    {
        // Конвертируем в dB для более точного расчета компрессии
        float inputDB = juce::Decibels::gainToDecibels(inputLevel, -96.0f);
        float threshDB = juce::Decibels::gainToDecibels(threshold, -96.0f);

        // Вычисляем подавление в dB
        float overThresholdDB = inputDB - threshDB;
        float gainReductionDB = overThresholdDB * (1.0f - 1.0f / ratio);

        // Конвертируем обратно в линейный коэффициент
        targetGain = juce::Decibels::decibelsToGain(-gainReductionDB);
        targetGain = juce::jlimit(0.01f, 1.0f, targetGain); // Минимум -40dB подавления
    }

    // 2. Моделируем оптическую ячейку
    // Оптическая ячейка реагирует на интенсивность света (пропорциональна входному уровню)
    float lightIntensity = 1.0f - targetGain; // Больше света = больше подавление

    // 3. Нелинейный Attack
    float attackTime = calculateAttackTime(inputLevel);
    float attackCoeff = calculateTimeConstant(attackTime);

    // Если нужно больше подавления (больше света), optoCellState увеличивается
    if (lightIntensity > optoCellState)
    {
        // Attack phase
        optoCellState = attackCoeff * optoCellState + (1.0f - attackCoeff) * lightIntensity;
    }
    else
    {
        // Release phase - многоступенчатый
        // Быстрый release для начальной фазы
        float fastReleaseCoeff = calculateTimeConstant(FAST_RELEASE_TIME);
        fastReleaseState = fastReleaseCoeff * fastReleaseState + (1.0f - fastReleaseCoeff) * lightIntensity;

        // Медленный release для хвоста
        float slowReleaseCoeff = calculateTimeConstant(SLOW_RELEASE_TIME);
        slowReleaseState = slowReleaseCoeff * slowReleaseState + (1.0f - slowReleaseCoeff) * lightIntensity;

        // Смешиваем быстрый и медленный release
        // В начале release доминирует быстрый компонент, затем медленный
        float releaseMix = RELEASE_BLEND;
        optoCellState = releaseMix * fastReleaseState + (1.0f - releaseMix) * slowReleaseState;
    }

    // 4. Преобразуем состояние оптической ячейки в gain reduction
    // Нелинейная характеристика фотодиода
    float optoCellResponse = optoCellState;

    // Добавляем нелинейность (логарифмическая характеристика)
    optoCellResponse = std::pow(optoCellResponse, 0.8f);

    currentGainReduction = 1.0f - optoCellResponse;
    currentGainReduction = juce::jlimit(0.01f, 1.0f, currentGainReduction); // Минимум -40dB

    return currentGainReduction;
}
