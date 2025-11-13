"""
Сервис для сопоставления (склейки) одинаковых товаров с разных маркетплейсов.

Алгоритм работает поэтапно с разными уровнями уверенности:
1. Прямое совпадение по GTIN (штрих-код) - confidence 1.0
2. Совпадение бренда + модели - confidence 0.95
3. Fuzzy matching по названию - confidence 0.80-0.90
4. Дополнительная валидация по атрибутам
"""
from typing import List, Dict, Set
from decimal import Decimal
import uuid
from collections import defaultdict

from ..models import Product, ProductMatch, MatchingMethod
from ..utils import calculate_similarity, compare_attributes
from ..config import settings


class MatcherService:
    """
    Сервис для сопоставления одинаковых товаров с разных площадок.
    """

    def __init__(self, min_similarity: float = None):
        """
        :param min_similarity: Минимальный порог similarity для fuzzy matching
        """
        self.min_similarity = min_similarity or settings.min_similarity_threshold

    def match_products(self, products: List[Product]) -> List[ProductMatch]:
        """
        Основной метод: группирует товары по совпадениям.

        Алгоритм (пошагово):
        1. Группируем по GTIN (если есть)
        2. Группируем по бренду + модели
        3. Fuzzy matching по названию для оставшихся
        4. Проверяем атрибуты для дополнительной валидации
        5. Создаём ProductMatch для каждой группы

        :param products: Список товаров с разных маркетплейсов
        :return: Список групп совпадающих товаров
        """
        if not products:
            return []

        # Шаг 1: Группировка по GTIN
        gtin_groups, remaining_products = self._match_by_gtin(products)

        # Шаг 2: Группировка по бренду + модели
        brand_model_groups, remaining_products = self._match_by_brand_model(
            remaining_products
        )

        # Шаг 3: Fuzzy matching по названию
        fuzzy_groups, _ = self._match_by_fuzzy_name(remaining_products)

        # Собираем все группы
        all_groups = []
        all_groups.extend(
            self._create_product_matches(gtin_groups, MatchingMethod.GTIN, 1.0)
        )
        all_groups.extend(
            self._create_product_matches(
                brand_model_groups, MatchingMethod.BRAND_MODEL, 0.95
            )
        )

        # Для fuzzy групп применяем валидацию по атрибутам
        for group in fuzzy_groups:
            # Вычисляем similarity для группы
            avg_similarity = self._calculate_group_similarity(group)
            # Бонус за совпадающие атрибуты
            attr_bonus = self._calculate_attribute_bonus(group)
            confidence = min(avg_similarity + attr_bonus, 1.0)

            if confidence >= self.min_similarity:
                match = self._create_product_match(
                    group, MatchingMethod.FUZZY_NAME, confidence
                )
                all_groups.append(match)

        return all_groups

    def _match_by_gtin(
        self, products: List[Product]
    ) -> tuple[List[List[Product]], List[Product]]:
        """
        Группировка по GTIN (Global Trade Item Number / штрих-код).

        Это самый точный метод - GTIN уникален для каждого товара.
        """
        gtin_map: Dict[str, List[Product]] = defaultdict(list)
        no_gtin: List[Product] = []

        for product in products:
            if product.gtin:
                gtin_map[product.gtin.strip().lower()].append(product)
            else:
                no_gtin.append(product)

        # Группы с минимум 2 товарами (иначе нет смысла в сопоставлении)
        groups = [group for group in gtin_map.values() if len(group) >= 2]

        # Товары с уникальным GTIN идут в оставшиеся
        for group in gtin_map.values():
            if len(group) == 1:
                no_gtin.extend(group)

        return groups, no_gtin

    def _match_by_brand_model(
        self, products: List[Product]
    ) -> tuple[List[List[Product]], List[Product]]:
        """
        Группировка по комбинации бренда и модели.

        Бренд + модель часто уникально идентифицируют товар.
        """
        brand_model_map: Dict[str, List[Product]] = defaultdict(list)
        no_brand_model: List[Product] = []

        for product in products:
            if product.brand and product.model:
                # Нормализуем для сравнения
                key = f"{product.brand.strip().lower()}_{product.model.strip().lower()}"
                brand_model_map[key].append(product)
            else:
                no_brand_model.append(product)

        groups = [group for group in brand_model_map.values() if len(group) >= 2]

        for group in brand_model_map.values():
            if len(group) == 1:
                no_brand_model.extend(group)

        return groups, no_brand_model

    def _match_by_fuzzy_name(
        self, products: List[Product]
    ) -> tuple[List[List[Product]], List[Product]]:
        """
        Группировка по fuzzy matching названий.

        Использует алгоритм вычисления similarity между названиями товаров.
        """
        if not products:
            return [], []

        # Будем использовать Union-Find для группировки
        # Для простоты используем списковый подход

        groups: List[List[Product]] = []
        used_indices: Set[int] = set()

        for i, product_a in enumerate(products):
            if i in used_indices:
                continue

            current_group = [product_a]
            used_indices.add(i)

            for j, product_b in enumerate(products[i + 1 :], start=i + 1):
                if j in used_indices:
                    continue

                similarity = calculate_similarity(product_a.name, product_b.name)

                if similarity >= self.min_similarity:
                    current_group.append(product_b)
                    used_indices.add(j)

            if len(current_group) >= 2:
                groups.append(current_group)

        # Непарные товары
        remaining = [p for i, p in enumerate(products) if i not in used_indices]

        return groups, remaining

    def _calculate_group_similarity(self, products: List[Product]) -> float:
        """
        Вычисляет среднюю similarity для группы товаров.
        """
        if len(products) < 2:
            return 0.0

        similarities = []

        for i, product_a in enumerate(products):
            for product_b in products[i + 1 :]:
                sim = calculate_similarity(product_a.name, product_b.name)
                similarities.append(sim)

        return sum(similarities) / len(similarities) if similarities else 0.0

    def _calculate_attribute_bonus(self, products: List[Product]) -> float:
        """
        Вычисляет бонус к confidence на основе совпадающих атрибутов.

        Если у товаров совпадают важные атрибуты (цвет, размер, материал),
        это увеличивает уверенность, что это один товар.
        """
        if len(products) < 2:
            return 0.0

        # Важные ключи атрибутов (можно расширить)
        important_keys = ["цвет", "размер", "материал", "объем", "вес"]

        attr_similarities = []

        for i, product_a in enumerate(products):
            for product_b in products[i + 1 :]:
                sim = compare_attributes(
                    product_a.attributes, product_b.attributes, important_keys
                )
                attr_similarities.append(sim)

        avg_attr_sim = (
            sum(attr_similarities) / len(attr_similarities)
            if attr_similarities
            else 0.0
        )

        # Бонус до 0.1
        return avg_attr_sim * 0.1

    def _create_product_matches(
        self,
        groups: List[List[Product]],
        method: MatchingMethod,
        confidence: float,
    ) -> List[ProductMatch]:
        """
        Создаёт ProductMatch объекты для групп.
        """
        return [
            self._create_product_match(group, method, confidence) for group in groups
        ]

    def _create_product_match(
        self, products: List[Product], method: MatchingMethod, confidence: float
    ) -> ProductMatch:
        """
        Создаёт ProductMatch для одной группы товаров.
        """
        # Сортируем по цене
        sorted_products = sorted(products, key=lambda p: p.price)

        cheapest = sorted_products[0]
        most_expensive = sorted_products[-1]

        price_diff = most_expensive.price - cheapest.price
        price_diff_percent = (
            (float(price_diff) / float(most_expensive.price)) * 100.0
            if most_expensive.price > 0
            else 0.0
        )

        avg_price = sum(p.price for p in products) / len(products)

        # Выбираем наиболее полное название
        representative_name = max(products, key=lambda p: len(p.name)).name

        # Бренд (берём первый непустой)
        representative_brand = next(
            (p.brand for p in products if p.brand), None
        )

        return ProductMatch(
            match_id=f"match_{uuid.uuid4().hex[:8]}",
            products=sorted_products,
            confidence=confidence,
            matching_method=method,
            cheapest_offer=cheapest,
            most_expensive_offer=most_expensive,
            price_difference=price_diff,
            price_difference_percent=price_diff_percent,
            avg_price=Decimal(str(avg_price)),
            representative_name=representative_name,
            representative_brand=representative_brand,
        )
