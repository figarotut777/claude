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
            period: Тип периода (today, week, month, all, custom)
            custom_start: Начальная дата для custom периода (ISO формат)
            custom_end: Конечная дата для custom периода (ISO формат)

        Returns:
            Кортеж (start_date, end_date) в ISO формате
        """
        # ИСПРАВЛЕНО: используем локальное время вместо UTC
        now = datetime.now()

        if period == 'today':
            # Для "сегодня" берём начало дня и конец дня
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        elif period == 'week':
            # Последние 7 дней (как на WB): сегодня минус 7 дней
            start_date = (now - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        elif period == 'month':
            # Последние 30 дней (как на WB): сегодня минус 30 дней
            start_date = (now - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        elif period == 'all':
            # За всё время - с момента начала данных WB API (29.01.2024)
            start_date = datetime(2024, 1, 29)
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
        Расчёт метрик за период (по Разделу 15.2 ТЗ)

        Args:
            period: Период (today, week, month, all, custom)
            custom_start: Начало custom периода
            custom_end: Конец custom периода
            nm_id: ID товара (если нужна статистика по одному товару)

        Returns:
            Словарь с метриками согласно ТЗ (Revenue Gross, Payout Net, Profit Net, ROI, Margin%, Tax)
        """
        self.logger.info(f"Расчёт метрик за период: {period}")

        # Получение дат периода
        start_date, end_date = self.get_period_dates(period, custom_start, custom_end)

        # Получение данных из БД
        sales = self.db.get_sales_for_period(start_date, end_date, nm_id)
        orders = self.db.get_orders_for_period(start_date, end_date, nm_id)

        # ГЛАВНОЕ: Получение финансового отчёта WB (содержит все расходы!)
        financial_report = self.db.get_financial_report_for_period(start_date, end_date, nm_id)

        # Получение информации о товарах
        if nm_id:
            products = [self.db.get_product_by_nm_id(nm_id)]
        else:
            products = self.db.get_products()

        # Создание мапы товаров для быстрого доступа
        products_map = {p['nm_id']: p for p in products if p}

        # Получение настроек (налоги)
        settings = self.db.get_settings()
        tax_rate = settings.get('tax_rate', 0.06)

        # Расчёт метрик из ФИНАНСОВОГО ОТЧЁТА WB (самые точные данные!)
        total_sales_qty = 0
        revenue_gross = 0  # Выручка валовая (retail_amount) - может быть N/A
        payout_net = 0  # К выплате от WB (ppvz_for_pay) - ВСЕГДА есть
        total_commission = 0  # Комиссия WB
        total_logistics = 0  # Логистика (доставка + возврат)
        total_storage = 0  # Хранение
        total_penalties = 0  # Штрафы
        total_returns = 0  # Возвраты (отдельно от логистики)
        total_ads = 0  # Реклама (пока 0, WB API не даёт)
        total_other = 0  # Прочие расходы
        total_cost = 0  # Себестоимость товаров (COGS)

        gross_available = False  # Флаг: доступна ли Revenue Gross

        for item in financial_report:
            qty = item.get('quantity', 0)
            doc_type = item.get('doc_type_name', '')

            # ИСПРАВЛЕНО: Обрабатываем ВСЕ записи, не только "Продажа"!
            # Расходы (хранение, штрафы) могут иметь пустой doc_type_name

            # К выплате от WB (может быть отрицательным для расходов!)
            to_pay = item.get('ppvz_for_pay', 0) or 0
            payout_net += to_pay

            # Хранение (ВСЕ записи, включая операции "Хранение")
            storage = item.get('storage_fee', 0) or 0
            total_storage += abs(storage)  # Хранение всегда положительное

            # Штрафы (ВСЕ записи)
            penalty = item.get('penalty', 0) or 0
            total_penalties += abs(penalty)

            # Логистика (ВСЕ записи)
            delivery = item.get('delivery_rub', 0) or 0
            total_logistics += abs(delivery)

            # Возвраты (отдельно)
            return_amount = item.get('return_amount', 0) or 0
            total_returns += abs(return_amount)

            # Только для продаж: считаем количество, выручку, комиссию, себестоимость
            if doc_type == 'Продажа':
                total_sales_qty += qty

                # Revenue Gross (retail_amount) - может отсутствовать!
                retail_amount = item.get('retail_amount', 0) or 0
                if retail_amount > 0:
                    revenue_gross += retail_amount
                    gross_available = True

                # Комиссия WB
                commission = item.get('ppvz_sales_commission', 0) or 0
                total_commission += abs(commission)

                # Себестоимость из настроек товара или истории
                product_nm_id = item.get('nm_id')
                sale_date = item.get('rr_dt', '')[:10] if item.get('rr_dt') else None

                if qty > 0 and product_nm_id:
                    # Получаем себестоимость на дату продажи
                    if sale_date:
                        cost_price = self.db.get_cost_price_at_date(product_nm_id, sale_date)
                    else:
                        cost_price = None

                    # Если нет в истории, берём из products
                    if cost_price is None:
                        product = products_map.get(product_nm_id)
                        cost_price = product.get('cost_price', 0) if product else 0

                    total_cost += (cost_price or 0) * qty

        # НАЛОГ (УСН) - рассчитывается от Revenue Gross
        tax = 0
        if gross_available and revenue_gross > 0:
            tax = revenue_gross * tax_rate

        # Total Expenses (ВСЕ расходы кроме COGS и налога)
        total_expenses = total_commission + total_logistics + total_storage + total_penalties + total_returns + total_ads + total_other

        # PROFIT NET (по формуле из ТЗ раздел 15.2)
        # Profit Net = Revenue Gross – Commission – Logistics – Storage – Returns – Fines – Ads – COGS – Taxes – Other
        # Если Revenue Gross недоступен, считаем от Payout Net
        if gross_available:
            profit_net = revenue_gross - total_commission - total_logistics - total_storage - total_penalties - total_returns - total_ads - total_cost - tax - total_other
        else:
            # Альтернативная формула: Payout Net - COGS - Tax
            profit_net = payout_net - total_cost - tax

        # ROI = Profit Net / COGS (N/A если COGS = 0)
        if total_cost > 0:
            roi = (profit_net / total_cost) * 100
            roi_available = True
        else:
            roi = 0
            roi_available = False

        # Margin% = Profit Net / Revenue Gross (N/A если Gross недоступен)
        if gross_available and revenue_gross > 0:
            margin_percent = (profit_net / revenue_gross) * 100
            margin_available = True
        else:
            margin_percent = 0
            margin_available = False

        # Расчёт метрик по заказам
        total_orders = len(orders)
        cancelled_orders = sum(1 for order in orders if order.get('is_cancel', 0))
        active_orders = total_orders - cancelled_orders

        # Средний чек
        avg_order_value = revenue_gross / total_sales_qty if total_sales_qty > 0 and gross_available else 0

        # Конверсия (продажи / заказы)
        conversion_rate = (total_sales_qty / total_orders * 100) if total_orders > 0 else 0

        metrics = {
            'period': {
                'type': period,
                'start': start_date,
                'end': end_date
            },
            'sales': {
                'quantity': total_sales_qty,
                'revenue_gross': round(revenue_gross, 2) if gross_available else None,
                'revenue_gross_available': gross_available,
                'payout_net': round(payout_net, 2),
                'avg_order_value': round(avg_order_value, 2)
            },
            'orders': {
                'total': total_orders,
                'active': active_orders,
                'cancelled': cancelled_orders,
                'conversion_rate': round(conversion_rate, 2)
            },
            'expenses': {
                'commission': round(total_commission, 2),
                'logistics': round(total_logistics, 2),
                'storage': round(total_storage, 2),
                'penalties': round(total_penalties, 2),
                'returns': round(total_returns, 2),
                'ads': round(total_ads, 2),
                'other': round(total_other, 2),
                'total_expenses': round(total_expenses, 2),
                'cogs': round(total_cost, 2)
            },
            'profit': {
                'cogs': round(total_cost, 2),
                'tax': round(tax, 2),
                'tax_rate': tax_rate,
                'profit_net': round(profit_net, 2),
                'roi': round(roi, 2) if roi_available else None,
                'roi_available': roi_available,
                'margin_percent': round(margin_percent, 2) if margin_available else None,
                'margin_available': margin_available
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

    def get_products_summary(self, period: str = 'month',
                            custom_start: str = None,
                            custom_end: str = None) -> List[Dict]:
        """
        Получение сводки по всем товарам с расчётом прибыли и статусов (по ТЗ раздел 15.4)

        Args:
            period: Период для расчёта метрик (today, week, month, custom)
            custom_start: Начало custom периода (ISO формат)
            custom_end: Конец custom периода (ISO формат)

        Returns:
            Список товаров с метриками: Profit Net, Revenue Gross, Margin%, ROI, статусы
        """
        products = self.db.get_products()
        stocks = self.db.get_latest_stocks()
        settings = self.db.get_settings()
        tax_rate = settings.get('tax_rate', 0.06)

        # Создание мапы остатков
        stocks_map = {}
        for stock in stocks:
            nm_id = stock['nm_id']
            if nm_id not in stocks_map:
                stocks_map[nm_id] = 0
            stocks_map[nm_id] += stock.get('quantity', 0)

        # Получение дат периода
        start_date, end_date = self.get_period_dates(period, custom_start, custom_end)

        # Сводка по каждому товару
        summary = []

        for product in products:
            nm_id = product['nm_id']

            # Получение финансового отчёта для товара
            financial_report = self.db.get_financial_report_for_period(start_date, end_date, nm_id)

            # Расчёт метрик аналогично calculate_metrics, но для отдельного товара
            total_sales_qty = 0
            return_qty = 0  # ИСПРАВЛЕНО: количество возвращённых товаров в штуках
            revenue_gross = 0
            payout_net = 0
            total_commission = 0
            total_logistics = 0
            total_storage = 0
            total_penalties = 0
            total_returns = 0  # Сумма возврата (в рублях)
            total_ads = 0
            total_other = 0
            total_cost = 0
            gross_available = False

            for item in financial_report:
                qty = item.get('quantity', 0)
                doc_type = item.get('doc_type_name', '')

                # К выплате
                to_pay = item.get('ppvz_for_pay', 0) or 0
                payout_net += to_pay

                # Расходы
                total_storage += abs(item.get('storage_fee', 0) or 0)
                total_penalties += abs(item.get('penalty', 0) or 0)
                total_logistics += abs(item.get('delivery_rub', 0) or 0)
                total_returns += abs(item.get('return_amount', 0) or 0)

                # Возвраты (ИСПРАВЛЕНО: считаем ШТУКИ, а не сумму)
                if doc_type == 'Возврат':
                    return_qty += abs(qty)  # Берём модуль, т.к. может быть отрицательным

                # Продажи
                if doc_type == 'Продажа':
                    total_sales_qty += qty

                    retail_amount = item.get('retail_amount', 0) or 0
                    if retail_amount > 0:
                        revenue_gross += retail_amount
                        gross_available = True

                    total_commission += abs(item.get('ppvz_sales_commission', 0) or 0)

                    # Себестоимость
                    sale_date = item.get('rr_dt', '')[:10] if item.get('rr_dt') else None
                    if qty > 0:
                        if sale_date:
                            cost_price = self.db.get_cost_price_at_date(nm_id, sale_date)
                        else:
                            cost_price = None

                        if cost_price is None:
                            cost_price = product.get('cost_price', 0) or 0

                        total_cost += cost_price * qty

            # Налог
            tax = revenue_gross * tax_rate if gross_available and revenue_gross > 0 else 0

            # Total Expenses
            total_expenses = total_commission + total_logistics + total_storage + total_penalties + total_returns + total_ads + total_other

            # Profit Net
            if gross_available:
                profit_net = revenue_gross - total_expenses - total_cost - tax
            else:
                profit_net = payout_net - total_cost - tax

            # ROI
            roi = (profit_net / total_cost * 100) if total_cost > 0 else None

            # Margin%
            margin_percent = (profit_net / revenue_gross * 100) if gross_available and revenue_gross > 0 else None

            # ПРОЦЕНТ ВОЗВРАТА (ИСПРАВЛЕНО: считаем из return_qty)
            return_percent = (return_qty / total_sales_qty * 100) if total_sales_qty > 0 else 0

            # Buyout % (TODO: считать из данных когда будут самовыкупы)
            buyout_percent = 0

            # DOS 14 (Days of Stock за 14 дней)
            # TODO: считать среднедневные продажи за 14 дней
            dos_14 = None

            # Остатки
            stock_qty = stocks_map.get(nm_id, 0)

            # СТАТУСЫ (раздел 15.4.1 ТЗ)
            statuses = []

            # NO_COGS: себестоимость не указана
            current_cost_price = self.db.get_current_cost_price(nm_id) or 0
            if current_cost_price == 0:
                statuses.append('NO_COGS')

            # GROSS_UNKNOWN: revenue_gross недоступен
            if not gross_available and total_sales_qty > 0:
                statuses.append('GROSS_UNKNOWN')

            # OOS: товар закончился
            if stock_qty == 0:
                statuses.append('OOS')

            # ABC class (TODO: реализовать классификацию)
            abc_class = None

            summary.append({
                'nm_id': nm_id,
                'article': product['article'],
                'name': product['name'],
                'brand': product['brand'],
                'subject': product.get('subject', ''),
                'image_url': product.get('image_url', ''),
                'statuses': statuses,
                'profit_net': round(profit_net, 2),
                'revenue_gross': round(revenue_gross, 2) if gross_available else None,
                'payout_net': round(payout_net, 2),
                'margin_percent': round(margin_percent, 2) if margin_percent is not None else None,
                'roi': round(roi, 2) if roi is not None else None,
                'cogs': round(total_cost, 2),
                'total_expenses': round(total_expenses, 2),
                'commission': round(total_commission, 2),
                'logistics': round(total_logistics, 2),
                'storage': round(total_storage, 2),
                'penalties': round(total_penalties, 2),
                'ads': round(total_ads, 2),
                'returns': round(total_returns, 2),
                'other': round(total_other, 2),
                'tax': round(tax, 2),
                'return_qty': return_qty,  # ДОБАВЛЕНО: количество возвратов в штуках
                'return_percent': round(return_percent, 2),  # ДОБАВЛЕНО: процент возврата
                'buyout_percent': buyout_percent,
                'dos_14': dos_14,
                'stock_qty': stock_qty,
                'sales_qty': total_sales_qty,
                'abc_class': abc_class,
                'cost_price': current_cost_price,
                'wb_commission': product.get('wb_commission_percent', 15)
            })

        # Сортировка по прибыли (убывание) - default sort
        summary.sort(key=lambda x: x['profit_net'], reverse=True)

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

    def get_top_profit(self, period: str = 'month', custom_start: str = None,
                      custom_end: str = None, limit: int = 10) -> List[Dict]:
        """
        Топ товаров по прибыли (раздел 15.5 ТЗ)

        Args:
            period: Период для расчёта
            custom_start: Начало custom периода
            custom_end: Конец custom периода
            limit: Количество товаров

        Returns:
            Список топ товаров по Profit Net
        """
        summary = self.get_products_summary(period=period, custom_start=custom_start, custom_end=custom_end)
        summary.sort(key=lambda x: x['profit_net'], reverse=True)
        return summary[:limit]

    def get_top_revenue(self, period: str = 'month', custom_start: str = None,
                       custom_end: str = None, limit: int = 10) -> List[Dict]:
        """
        Топ товаров по выручке (раздел 15.5 ТЗ)

        Args:
            period: Период для расчёта
            custom_start: Начало custom периода
            custom_end: Конец custom периода
            limit: Количество товаров

        Returns:
            Список топ товаров по Revenue Gross
        """
        summary = self.get_products_summary(period=period, custom_start=custom_start, custom_end=custom_end)
        # Фильтруем товары с доступной Revenue Gross
        with_revenue = [p for p in summary if p['revenue_gross'] is not None and p['revenue_gross'] > 0]
        with_revenue.sort(key=lambda x: x['revenue_gross'], reverse=True)
        return with_revenue[:limit]

    def get_worst_profit(self, period: str = 'month', custom_start: str = None,
                        custom_end: str = None, limit: int = 10) -> List[Dict]:
        """
        Худшие товары по прибыли (раздел 15.5 ТЗ)

        Args:
            period: Период для расчёта
            custom_start: Начало custom периода
            custom_end: Конец custom периода
            limit: Количество товаров

        Returns:
            Список худших товаров по Profit Net
        """
        summary = self.get_products_summary(period=period, custom_start=custom_start, custom_end=custom_end)
        summary.sort(key=lambda x: x['profit_net'])  # По возрастанию (худшие первые)
        return summary[:limit]

    def get_fastest_change(self, period: str = 'month', custom_start: str = None,
                          custom_end: str = None, limit: int = 10) -> List[Dict]:
        """
        Товары с самым быстрым изменением прибыли (раздел 15.5 ТЗ)

        Args:
            period: Период для расчёта
            custom_start: Начало custom периода
            custom_end: Конец custom периода
            limit: Количество товаров

        Returns:
            Список товаров с наибольшим |Δ Profit Net %|
        """
        # Получаем данные за текущий период
        current_summary = self.get_products_summary(period=period, custom_start=custom_start, custom_end=custom_end)

        # Получаем данные за предыдущий период той же длительности
        start_date, end_date = self.get_period_dates(period, custom_start, custom_end)
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        period_duration = end_dt - start_dt

        prev_start_dt = start_dt - period_duration
        prev_end_dt = start_dt

        # Для предыдущего периода используем custom период
        prev_summary = self.get_products_summary(
            period='custom',
            custom_start=prev_start_dt.isoformat(),
            custom_end=prev_end_dt.isoformat()
        )

        # Создаём мапу предыдущих значений прибыли по nm_id
        prev_profit_map = {p['nm_id']: p.get('profit_net', 0) for p in prev_summary}

        # Рассчитываем процентное изменение прибыли
        for product in current_summary:
            nm_id = product['nm_id']
            current_profit = product.get('profit_net', 0)
            prev_profit = prev_profit_map.get(nm_id, 0)

            # Расчёт процентного изменения
            if prev_profit != 0:
                change_percent = ((current_profit - prev_profit) / abs(prev_profit)) * 100
            elif current_profit != 0:
                change_percent = 100  # Если была 0, а стала положительная - 100% рост
            else:
                change_percent = 0

            product['profit_change_percent'] = round(change_percent, 2)

        # Сортируем по абсолютному значению изменения
        current_summary.sort(key=lambda x: abs(x.get('profit_change_percent', 0)), reverse=True)

        return current_summary[:limit]

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

        # Топ товаров (старый формат для совместимости)
        top_products = self.get_top_products(period=period, limit=5)

        # Сводка по товарам (с новыми метриками) - ИСПРАВЛЕНО: передаём custom даты
        products_summary = self.get_products_summary(period=period, custom_start=custom_start, custom_end=custom_end)

        # TOP BLOCKS (раздел 15.5 ТЗ) - ИСПРАВЛЕНО: передаём custom даты
        top_blocks = {
            'top_profit': self.get_top_profit(period=period, custom_start=custom_start, custom_end=custom_end, limit=10),
            'top_revenue': self.get_top_revenue(period=period, custom_start=custom_start, custom_end=custom_end, limit=10),
            'worst_profit': self.get_worst_profit(period=period, custom_start=custom_start, custom_end=custom_end, limit=10),
            'fastest_change': self.get_fastest_change(period=period, custom_start=custom_start, custom_end=custom_end, limit=10)
        }

        # Текущие остатки
        stocks = self.db.get_latest_stocks()

        # Статистика по остаткам
        total_stock_qty = sum(stock.get('quantity', 0) or 0 for stock in stocks)
        total_stock_value = sum(
            (stock.get('quantity') or 0) * (stock.get('price') or 0)
            for stock in stocks
        )

        # Информация о последнем обновлении (ИСПРАВЛЕНО: ключ должен быть last_incremental_sync)
        sync_status = {
            'last_incremental_sync': self.db.get_metadata('last_incremental_sync'),
            'total_products': len(self.db.get_products())
        }

        # Настройки (для передачи в UI)
        settings = self.db.get_settings()

        dashboard_data = {
            'metrics': metrics,
            'top_products': top_products,
            'products_summary': products_summary,
            'top_blocks': top_blocks,
            'stocks': {
                'total_quantity': total_stock_qty,
                'total_value': round(total_stock_value, 2),
                'items_count': len(stocks)
            },
            'settings': settings,
            'sync_status': sync_status,
            'generated_at': datetime.now().isoformat()
        }

        return dashboard_data
