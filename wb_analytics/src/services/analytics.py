"""
Модуль аналитики для расчёта метрик по продажам Wildberries
Рассчитывает: продажи, выручку, прибыль, тренды и другие KPI
"""

import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database.models import DatabaseManager


class AnalyticsService:
    """Сервис для расчёта аналитических метрик"""

    def __init__(self, db_path: str = "data/wb_analytics.db"):
        """
        Инициализация сервиса аналитики

        Args:
            db_path: Путь к базе данных
        """
        self.logger = logging.getLogger(__name__)
        self.db = DatabaseManager(db_path=db_path)

    def get_period_dates(self, period: str, custom_start: str = None,
                        custom_end: str = None) -> Tuple[str, str]:
        """
        Получение дат начала и конца периода

        Args:
            period: Тип периода (today, week, month, custom)
            custom_start: Начальная дата для custom периода (ISO формат)
            custom_end: Конечная дата для custom периода (ISO формат)

        Returns:
            Кортеж (start_date, end_date) в ISO формате
        """
        now = datetime.utcnow()

        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now

        elif period == 'week':
            start_date = now - timedelta(days=7)
            end_date = now

        elif period == 'month':
            start_date = now - timedelta(days=30)
            end_date = now

        elif period == 'custom':
            if not custom_start or not custom_end:
                raise ValueError("Для custom периода нужны custom_start и custom_end")
            start_date = datetime.fromisoformat(custom_start.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(custom_end.replace('Z', '+00:00'))

        else:
            raise ValueError(f"Неизвестный период: {period}")

        return start_date.isoformat(), end_date.isoformat()

    def calculate_metrics(self, period: str = 'today',
                         custom_start: str = None,
                         custom_end: str = None,
                         nm_id: int = None) -> Dict:
        """
        Расчёт метрик за период

        Args:
            period: Период (today, week, month, custom)
            custom_start: Начало custom периода
            custom_end: Конец custom периода
            nm_id: ID товара (если нужна статистика по одному товару)

        Returns:
            Словарь с метриками
        """
        self.logger.info(f"Расчёт метрик за период: {period}")

        # Получение дат периода
        start_date, end_date = self.get_period_dates(period, custom_start, custom_end)

        # Получение данных из БД
        sales = self.db.get_sales_for_period(start_date, end_date, nm_id)
        orders = self.db.get_orders_for_period(start_date, end_date, nm_id)

        # Получение информации о товарах
        if nm_id:
            products = [self.db.get_product_by_nm_id(nm_id)]
        else:
            products = self.db.get_products()

        # Создание мапы товаров для быстрого доступа
        products_map = {p['nm_id']: p for p in products if p}

        # Расчёт основных метрик
        total_sales_qty = len(sales)
        total_sales_revenue = sum(sale.get('forPay', 0) or 0 for sale in sales)

        # Расчёт выручки после комиссии WB
        revenue_after_commission = 0
        total_cost = 0
        net_profit = 0

        for sale in sales:
            sale_nm_id = sale.get('nm_id')
            product = products_map.get(sale_nm_id)

            if product:
                # Выручка с продажи
                sale_revenue = sale.get('forPay', 0) or 0

                # Комиссия WB
                wb_commission_percent = product.get('wb_commission_percent', 15)
                commission_amount = sale_revenue * (wb_commission_percent / 100)

                # Выручка после комиссии
                revenue_after_comm = sale_revenue - commission_amount
                revenue_after_commission += revenue_after_comm

                # Себестоимость
                cost_price = product.get('cost_price', 0)
                total_cost += cost_price

                # Чистая прибыль = Выручка после комиссии - Себестоимость
                net_profit += (revenue_after_comm - cost_price)

        # Расчёт метрик по заказам
        total_orders = len(orders)
        cancelled_orders = sum(1 for order in orders if order.get('is_cancel', 0))
        active_orders = total_orders - cancelled_orders

        # Средний чек
        avg_order_value = total_sales_revenue / total_sales_qty if total_sales_qty > 0 else 0

        # Конверсия (продажи / заказы)
        conversion_rate = (total_sales_qty / total_orders * 100) if total_orders > 0 else 0

        # Рентабельность (прибыль / выручка)
        roi = (net_profit / total_sales_revenue * 100) if total_sales_revenue > 0 else 0

        metrics = {
            'period': {
                'type': period,
                'start': start_date,
                'end': end_date
            },
            'sales': {
                'quantity': total_sales_qty,
                'revenue': round(total_sales_revenue, 2),
                'revenue_after_commission': round(revenue_after_commission, 2),
                'avg_order_value': round(avg_order_value, 2)
            },
            'orders': {
                'total': total_orders,
                'active': active_orders,
                'cancelled': cancelled_orders,
                'conversion_rate': round(conversion_rate, 2)
            },
            'profit': {
                'total_cost': round(total_cost, 2),
                'net_profit': round(net_profit, 2),
                'roi': round(roi, 2)
            }
        }

        # Расчёт трендов (сравнение с предыдущим периодом)
        trends = self._calculate_trends(start_date, end_date, nm_id)
        metrics['trends'] = trends

        return metrics

    def _calculate_trends(self, start_date: str, end_date: str,
                         nm_id: int = None) -> Dict:
        """
        Расчёт трендов (изменение метрик по сравнению с предыдущим периодом)

        Args:
            start_date: Начало текущего периода
            end_date: Конец текущего периода
            nm_id: ID товара (опционально)

        Returns:
            Словарь с процентными изменениями
        """
        # Вычисление длительности периода
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        period_duration = end_dt - start_dt

        # Получение данных за предыдущий период
        prev_start_dt = start_dt - period_duration
        prev_end_dt = start_dt

        prev_start = prev_start_dt.isoformat()
        prev_end = prev_end_dt.isoformat()

        # Текущий период
        current_sales = self.db.get_sales_for_period(start_date, end_date, nm_id)
        current_revenue = sum(sale.get('forPay', 0) or 0 for sale in current_sales)
        current_qty = len(current_sales)

        # Предыдущий период
        prev_sales = self.db.get_sales_for_period(prev_start, prev_end, nm_id)
        prev_revenue = sum(sale.get('forPay', 0) or 0 for sale in prev_sales)
        prev_qty = len(prev_sales)

        # Расчёт процентных изменений
        revenue_change = self._calculate_percentage_change(prev_revenue, current_revenue)
        qty_change = self._calculate_percentage_change(prev_qty, current_qty)

        return {
            'revenue_change_percent': round(revenue_change, 2),
            'quantity_change_percent': round(qty_change, 2),
            'previous_period': {
                'start': prev_start,
                'end': prev_end,
                'revenue': round(prev_revenue, 2),
                'quantity': prev_qty
            }
        }

    def _calculate_percentage_change(self, old_value: float, new_value: float) -> float:
        """
        Расчёт процентного изменения

        Args:
            old_value: Старое значение
            new_value: Новое значение

        Returns:
            Процентное изменение
        """
        if old_value == 0:
            return 100.0 if new_value > 0 else 0.0

        return ((new_value - old_value) / old_value) * 100

    def get_products_summary(self) -> List[Dict]:
        """
        Получение сводки по всем товарам

        Returns:
            Список товаров с основными метриками
        """
        products = self.db.get_products()
        stocks = self.db.get_latest_stocks()

        # Создание мапы остатков
        stocks_map = {}
        for stock in stocks:
            nm_id = stock['nm_id']
            if nm_id not in stocks_map:
                stocks_map[nm_id] = 0
            stocks_map[nm_id] += stock.get('quantity', 0)

        # Сводка по каждому товару
        summary = []

        for product in products:
            nm_id = product['nm_id']

            # Получение продаж за последние 30 дней
            start_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
            end_date = datetime.utcnow().isoformat()

            sales = self.db.get_sales_for_period(start_date, end_date, nm_id)

            total_sales_qty = len(sales)
            total_revenue = sum(sale.get('forPay', 0) or 0 for sale in sales)

            # Остатки
            stock_qty = stocks_map.get(nm_id, 0)

            summary.append({
                'nm_id': nm_id,
                'article': product['article'],
                'name': product['name'],
                'brand': product['brand'],
                'sales_qty_30d': total_sales_qty,
                'revenue_30d': round(total_revenue, 2),
                'stock_qty': stock_qty,
                'cost_price': product.get('cost_price', 0),
                'wb_commission': product.get('wb_commission_percent', 15)
            })

        # Сортировка по выручке (убывание)
        summary.sort(key=lambda x: x['revenue_30d'], reverse=True)

        return summary

    def get_top_products(self, period: str = 'month', limit: int = 10) -> List[Dict]:
        """
        Получение топ товаров по продажам

        Args:
            period: Период (today, week, month)
            limit: Количество товаров в топе

        Returns:
            Список топ товаров
        """
        start_date, end_date = self.get_period_dates(period)

        # Получение всех продаж
        sales = self.db.get_sales_for_period(start_date, end_date)

        # Группировка по товарам
        products_stats = {}

        for sale in sales:
            nm_id = sale.get('nm_id')
            revenue = sale.get('forPay', 0) or 0

            if nm_id not in products_stats:
                products_stats[nm_id] = {
                    'nm_id': nm_id,
                    'quantity': 0,
                    'revenue': 0
                }

            products_stats[nm_id]['quantity'] += 1
            products_stats[nm_id]['revenue'] += revenue

        # Получение информации о товарах
        products_list = []
        for nm_id, stats in products_stats.items():
            product = self.db.get_product_by_nm_id(nm_id)
            if product:
                products_list.append({
                    'nm_id': nm_id,
                    'article': product['article'],
                    'name': product['name'],
                    'brand': product['brand'],
                    'quantity': stats['quantity'],
                    'revenue': round(stats['revenue'], 2)
                })

        # Сортировка по выручке
        products_list.sort(key=lambda x: x['revenue'], reverse=True)

        return products_list[:limit]

    def get_dashboard_data(self, period: str = 'today',
                          custom_start: str = None,
                          custom_end: str = None) -> Dict:
        """
        Получение всех данных для дашборда

        Args:
            period: Период для отображения
            custom_start: Начало кастомного периода
            custom_end: Конец кастомного периода

        Returns:
            Полный набор данных для дашборда
        """
        self.logger.info(f"Генерация данных дашборда за период: {period}")

        # Основные метрики
        metrics = self.calculate_metrics(
            period=period,
            custom_start=custom_start,
            custom_end=custom_end
        )

        # Топ товаров
        top_products = self.get_top_products(period=period, limit=5)

        # Сводка по товарам
        products_summary = self.get_products_summary()

        # Текущие остатки
        stocks = self.db.get_latest_stocks()

        # Статистика по остаткам
        total_stock_qty = sum(stock.get('quantity', 0) for stock in stocks)
        total_stock_value = sum(
            stock.get('quantity', 0) * stock.get('price', 0)
            for stock in stocks
        )

        # Информация о последнем обновлении
        sync_status = {
            'last_update': self.db.get_metadata('last_incremental_sync'),
            'total_products': len(self.db.get_products())
        }

        dashboard_data = {
            'metrics': metrics,
            'top_products': top_products,
            'products_summary': products_summary,
            'stocks': {
                'total_quantity': total_stock_qty,
                'total_value': round(total_stock_value, 2),
                'items_count': len(stocks)
            },
            'sync_status': sync_status,
            'generated_at': datetime.utcnow().isoformat()
        }

        return dashboard_data
