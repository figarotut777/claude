"""
Утилиты для сравнения текстов и fuzzy matching.
"""
import re
from typing import Set, List
from rapidfuzz import fuzz


# Стоп-слова для русского языка (слова, которые не влияют на суть товара)
STOP_WORDS: Set[str] = {
    "купить",
    "заказать",
    "скидка",
    "распродажа",
    "новинка",
    "акция",
    "бесплатная",
    "доставка",
    "официальный",
    "оригинал",
    "оригинальный",
    "магазин",
    "интернет",
    "недорого",
    "дешево",
    "качественный",
    "лучший",
    "топ",
    "хит",
    "продаж",
    "new",
    "sale",
    "free",
}


def normalize_text(text: str) -> str:
    """
    Нормализация текста для сравнения.

    - Приведение к нижнему регистру
    - Удаление лишних пробелов
    - Удаление специальных символов (кроме букв, цифр, пробелов)
    """
    if not text:
        return ""

    # Lowercase
    text = text.lower()

    # Удаляем всё кроме букв, цифр и пробелов
    text = re.sub(r"[^\w\s]", " ", text)

    # Множественные пробелы -> один пробел
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def remove_stop_words(text: str, stop_words: Set[str] = STOP_WORDS) -> str:
    """
    Удаляет стоп-слова из текста.
    """
    words = text.split()
    filtered_words = [w for w in words if w not in stop_words]
    return " ".join(filtered_words)


def prepare_for_comparison(text: str) -> str:
    """
    Полная подготовка текста для сравнения.

    Применяет нормализацию и удаление стоп-слов.
    """
    text = normalize_text(text)
    text = remove_stop_words(text)
    return text


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Вычисляет similarity между двумя текстами (0.0 - 1.0).

    Использует комбинацию нескольких метрик из rapidfuzz:
    - token_sort_ratio: сравнение с учётом порядка слов
    - partial_ratio: частичное совпадение
    - ratio: простое сравнение

    Возвращает среднее значение, нормализованное к диапазону 0.0-1.0.
    """
    if not text1 or not text2:
        return 0.0

    # Подготовка текстов
    prepared1 = prepare_for_comparison(text1)
    prepared2 = prepare_for_comparison(text2)

    # Если после подготовки тексты пустые
    if not prepared1 or not prepared2:
        return 0.0

    # Используем несколько метрик и берём среднее
    token_sort = fuzz.token_sort_ratio(prepared1, prepared2)
    partial = fuzz.partial_ratio(prepared1, prepared2)
    simple = fuzz.ratio(prepared1, prepared2)

    # Среднее арифметическое, нормализуем к 0.0-1.0
    avg_score = (token_sort + partial + simple) / 3.0
    return avg_score / 100.0


def extract_brand_and_model(product_name: str) -> tuple[str | None, str | None]:
    """
    Пытается извлечь бренд и модель из названия товара.

    Эвристика: первое слово обычно бренд, остальное - модель/описание.

    Для продакшена стоит использовать ML или словари брендов.
    """
    normalized = normalize_text(product_name)
    words = normalized.split()

    if len(words) == 0:
        return None, None

    if len(words) == 1:
        return words[0], None

    # Простая эвристика: первое слово - бренд
    brand = words[0]

    # Ищем модель (обычно содержит цифры или имеет специфический формат)
    model_candidates = [w for w in words[1:] if any(c.isdigit() for c in w)]

    if model_candidates:
        model = model_candidates[0]
    else:
        # Если модели с цифрами нет, берём второе слово
        model = words[1] if len(words) > 1 else None

    return brand, model


def compare_attributes(
    attrs1: dict[str, any],
    attrs2: dict[str, any],
    important_keys: List[str] = None,
) -> float:
    """
    Сравнивает словари атрибутов товаров.

    Возвращает долю совпадающих атрибутов (0.0 - 1.0).

    :param attrs1: Атрибуты первого товара
    :param attrs2: Атрибуты второго товара
    :param important_keys: Ключи, которые важны для сравнения
    :return: Similarity score
    """
    if not attrs1 or not attrs2:
        return 0.0

    # Если не указаны важные ключи, используем пересечение ключей
    if important_keys is None:
        important_keys = list(set(attrs1.keys()) & set(attrs2.keys()))

    if not important_keys:
        return 0.0

    matches = 0
    total = len(important_keys)

    for key in important_keys:
        val1 = attrs1.get(key)
        val2 = attrs2.get(key)

        if val1 is None or val2 is None:
            continue

        # Сравниваем значения (с нормализацией для строк)
        if isinstance(val1, str) and isinstance(val2, str):
            val1_norm = normalize_text(val1)
            val2_norm = normalize_text(val2)
            if val1_norm == val2_norm:
                matches += 1
        elif val1 == val2:
            matches += 1

    return matches / total if total > 0 else 0.0
