#pragma once

#include <juce_core/juce_core.h>
#include <cmath>

/**
 * OptoCell - Моделирует оптоэлектронный аттенюатор (Opto-Cell) LA-2A
 *
 * Особенности:
 * - Нелинейное время Attack и Release зависят от входной амплитуды
 * - Многоступенчатая кривая Release (быстрый начальный сброс + медленный хвост)
 * - Эмуляция фотодиода и светоизлучающего элемента
 */
class OptoCell
{
public:
    OptoCell();

    void prepare(double sampleRate);
    void reset();

    /**
     * Обрабатывает один сэмпл
     * @param inputLevel - детектированный уровень входного сигнала (линейный)
     * @param peakReduction - параметр Peak Reduction (0-1)
     * @param isLimitMode - режим Limit (true) или Compress (false)
     * @return коэффициент подавления усиления (0-1, где 1 = без подавления)
     */
    float processSample(float inputLevel, float peakReduction, bool isLimitMode);

    float getCurrentGainReduction() const { return currentGainReduction; }

private:
    // Состояние оптической ячейки
    float optoCellState = 0.0f;     // Текущее состояние фотодиода (0-1)
    float currentGainReduction = 1.0f; // Текущее подавление усиления

    // Многоступенчатый release
    float fastReleaseState = 0.0f;
    float slowReleaseState = 0.0f;

    double sampleRate = 44100.0;

    // Параметры времени (в секундах)
    static constexpr float MIN_ATTACK_TIME = 0.001f;   // 1ms
    static constexpr float MAX_ATTACK_TIME = 0.010f;   // 10ms
    static constexpr float FAST_RELEASE_TIME = 0.060f;  // 60ms
    static constexpr float SLOW_RELEASE_TIME = 2.0f;    // 2s
    static constexpr float RELEASE_BLEND = 0.7f;        // Смешивание быстрого/медленного release

    // Вычисляет нелинейное время attack на основе входного уровня
    float calculateAttackTime(float inputLevel);

    // Вычисляет коэффициенты сглаживания
    float calculateTimeConstant(float timeInSeconds);
};
