"""
Flask сервер для Web Dashboard
Предоставляет API endpoints для получения аналитических данных
"""

import os
import sys
import logging
from pathlib import Path
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS

# Добавление корневой директории в путь
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.services.analytics import AnalyticsService
from src.database.models import DatabaseManager


# Инициализация Flask приложения
app = Flask(__name__,
           template_folder='../../templates',
           static_folder='../../static')

# Включение CORS для API
CORS(app)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация сервисов
DB_PATH = os.getenv('DB_PATH', 'wb_analytics/data/wb_analytics.db')
analytics_service = AnalyticsService(db_path=DB_PATH)
db_manager = DatabaseManager(db_path=DB_PATH)


@app.route('/')
def index():
    """Главная страница дашборда"""
    return render_template('dashboard.html')


@app.route('/api/health')
def health_check():
    """Проверка работоспособности API"""
    return jsonify({
        'status': 'ok',
        'message': 'WB Analytics API is running'
    })


@app.route('/api/dashboard')
def get_dashboard_data():
    """
    Получение данных для дашборда

    Query параметры:
        period: Период (today, week, month, custom)
        start: Начало периода для custom (ISO формат)
        end: Конец периода для custom (ISO формат)
    """
    try:
        period = request.args.get('period', 'today')
        custom_start = request.args.get('start')
        custom_end = request.args.get('end')

        logger.info(f"Запрос данных дашборда: period={period}")

        if period == 'custom':
            if not custom_start or not custom_end:
                return jsonify({
                    'error': 'Для custom периода нужны параметры start и end'
                }), 400

            data = analytics_service.get_dashboard_data(period=period)
        else:
            data = analytics_service.get_dashboard_data(period=period)

        return jsonify(data)

    except Exception as e:
        logger.error(f"Ошибка при получении данных дашборда: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/metrics')
def get_metrics():
    """
    Получение метрик за период

    Query параметры:
        period: Период (today, week, month, custom)
        start: Начало периода для custom
        end: Конец периода для custom
        nm_id: ID товара (опционально)
    """
    try:
        period = request.args.get('period', 'today')
        custom_start = request.args.get('start')
        custom_end = request.args.get('end')
        nm_id = request.args.get('nm_id', type=int)

        logger.info(f"Запрос метрик: period={period}, nm_id={nm_id}")

        metrics = analytics_service.calculate_metrics(
            period=period,
            custom_start=custom_start,
            custom_end=custom_end,
            nm_id=nm_id
        )

        return jsonify(metrics)

    except Exception as e:
        logger.error(f"Ошибка при расчёте метрик: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/products')
def get_products():
    """Получение списка товаров с метриками"""
    try:
        logger.info("Запрос списка товаров")

        products = analytics_service.get_products_summary()

        return jsonify({
            'products': products,
            'total': len(products)
        })

    except Exception as e:
        logger.error(f"Ошибка при получении товаров: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/<int:nm_id>')
def get_product_details(nm_id):
    """
    Получение детальной информации о товаре

    Args:
        nm_id: ID товара
    """
    try:
        logger.info(f"Запрос детальной информации о товаре {nm_id}")

        product = db_manager.get_product_by_nm_id(nm_id)

        if not product:
            return jsonify({'error': 'Товар не найден'}), 404

        # Метрики за последние 30 дней
        metrics = analytics_service.calculate_metrics(
            period='month',
            nm_id=nm_id
        )

        return jsonify({
            'product': product,
            'metrics': metrics
        })

    except Exception as e:
        logger.error(f"Ошибка при получении товара {nm_id}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/<int:nm_id>/settings', methods=['PUT'])
def update_product_settings(nm_id):
    """
    Обновление настроек товара (себестоимость, комиссия)

    Body:
        {
            "cost_price": 500.0,
            "wb_commission": 15.0
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Нет данных для обновления'}), 400

        cost_price = data.get('cost_price')
        wb_commission = data.get('wb_commission')

        logger.info(f"Обновление настроек товара {nm_id}")

        success = db_manager.update_product_settings(
            nm_id=nm_id,
            cost_price=cost_price,
            wb_commission=wb_commission
        )

        if success:
            return jsonify({
                'success': True,
                'message': 'Настройки товара обновлены'
            })
        else:
            return jsonify({'error': 'Товар не найден'}), 404

    except Exception as e:
        logger.error(f"Ошибка при обновлении товара {nm_id}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/top-products')
def get_top_products():
    """
    Получение топ товаров по продажам

    Query параметры:
        period: Период (today, week, month)
        limit: Количество товаров (по умолчанию 10)
    """
    try:
        period = request.args.get('period', 'month')
        limit = request.args.get('limit', 10, type=int)

        logger.info(f"Запрос топ товаров: period={period}, limit={limit}")

        top_products = analytics_service.get_top_products(
            period=period,
            limit=limit
        )

        return jsonify({
            'products': top_products,
            'period': period
        })

    except Exception as e:
        logger.error(f"Ошибка при получении топ товаров: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/stocks')
def get_stocks():
    """Получение актуальных остатков"""
    try:
        logger.info("Запрос данных об остатках")

        stocks = db_manager.get_latest_stocks()

        return jsonify({
            'stocks': stocks,
            'total': len(stocks)
        })

    except Exception as e:
        logger.error(f"Ошибка при получении остатков: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/sync-status')
def get_sync_status():
    """Получение статуса синхронизации данных"""
    try:
        status = {
            'last_incremental_sync': db_manager.get_metadata('last_incremental_sync'),
            'last_full_sync': db_manager.get_metadata('last_full_sync'),
            'total_products': len(db_manager.get_products())
        }

        return jsonify(status)

    except Exception as e:
        logger.error(f"Ошибка при получении статуса синхронизации: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Обработчик ошибки 404"""
    return jsonify({'error': 'Endpoint не найден'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Обработчик ошибки 500"""
    logger.error(f"Внутренняя ошибка сервера: {error}")
    return jsonify({'error': 'Внутренняя ошибка сервера'}), 500


if __name__ == '__main__':
    # Запуск сервера
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'

    logger.info(f"Запуск WB Analytics Server на порту {port}")
    logger.info(f"Debug режим: {debug}")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
