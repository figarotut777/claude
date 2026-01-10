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
from dotenv import load_dotenv

# Добавление корневой директории в путь
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Загрузка переменных окружения из .env
env_path = ROOT_DIR / '.env'
if env_path.exists():
    load_dotenv(env_path)

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


@app.route('/cost-prices')
def cost_prices_page():
    """Страница управления себестоимостью"""
    return render_template('cost_prices.html')


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

        # Получение данных дашборда с учётом кастомного периода
        if period == 'custom':
            if not custom_start or not custom_end:
                return jsonify({
                    'error': 'Для custom периода нужны параметры start и end'
                }), 400

        # Вызов с параметрами для всех случаев
        data = analytics_service.get_dashboard_data(
            period=period,
            custom_start=custom_start,
            custom_end=custom_end
        )

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


@app.route('/api/cost-prices', methods=['GET', 'POST'])
def manage_cost_prices():
    """
    Получение списка товаров с себестоимостью или обновление себестоимости

    GET: возвращает все товары с текущей себестоимостью
    POST: обновляет себестоимость для товара

    Body (для POST):
        {
            "nm_id": 123456789,
            "cost_price": 500.0,
            "valid_from": "2025-01-09" (опционально)
        }
    """
    try:
        if request.method == 'GET':
            # Получение всех товаров с себестоимостью
            products = db_manager.get_products()

            products_with_costs = []
            for product in products:
                cost_price = db_manager.get_current_cost_price(product['nm_id'])
                products_with_costs.append({
                    **product,
                    'cost_price': cost_price
                })

            return jsonify({
                'products': products_with_costs,
                'total': len(products_with_costs)
            })

        elif request.method == 'POST':
            # Обновление себестоимости
            data = request.get_json()

            if not data or 'nm_id' not in data or 'cost_price' not in data:
                return jsonify({'error': 'Не указан nm_id или cost_price'}), 400

            nm_id = data.get('nm_id')
            cost_price = data.get('cost_price')
            valid_from = data.get('valid_from')

            # Проверка что товар существует
            product = db_manager.get_product_by_nm_id(nm_id)
            if not product:
                return jsonify({'error': 'Товар не найден'}), 404

            logger.info(f"Обновление себестоимости товара {nm_id}: {cost_price} ₽")

            # Обновление через историческую таблицу
            record_id = db_manager.update_cost_price(
                nm_id=nm_id,
                cost_price=cost_price,
                valid_from=valid_from
            )

            return jsonify({
                'success': True,
                'message': 'Себестоимость обновлена',
                'record_id': record_id,
                'nm_id': nm_id,
                'cost_price': cost_price
            })

    except Exception as e:
        logger.error(f"Ошибка при работе с себестоимостью: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/<int:nm_id>/cost-price', methods=['PATCH'])
def update_product_cost_price(nm_id):
    """
    Обновление себестоимости товара с историей (раздел 15.4.2 ТЗ)

    Body:
        {
            "cost_price": 500.0,
            "valid_from": "2025-01-09" (опционально, по умолчанию сегодня)
        }
    """
    try:
        data = request.get_json()

        if not data or 'cost_price' not in data:
            return jsonify({'error': 'Не указана себестоимость (cost_price)'}), 400

        cost_price = data.get('cost_price')
        valid_from = data.get('valid_from')  # Опционально

        # Проверка что товар существует
        product = db_manager.get_product_by_nm_id(nm_id)
        if not product:
            return jsonify({'error': 'Товар не найден'}), 404

        logger.info(f"Обновление себестоимости товара {nm_id}: {cost_price} ₽ с {valid_from or 'сегодня'}")

        # Обновление через историческую таблицу
        record_id = db_manager.update_cost_price(
            nm_id=nm_id,
            cost_price=cost_price,
            valid_from=valid_from
        )

        return jsonify({
            'success': True,
            'message': 'Себестоимость обновлена',
            'record_id': record_id,
            'nm_id': nm_id,
            'cost_price': cost_price,
            'valid_from': valid_from
        })

    except Exception as e:
        logger.error(f"Ошибка при обновлении себестоимости товара {nm_id}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings', methods=['GET', 'PATCH'])
def manage_settings():
    """
    Получение или обновление глобальных настроек (раздел 15.1 ТЗ)

    GET: возвращает текущие настройки
    PATCH: обновляет настройки

    Body (для PATCH):
        {
            "tax_mode": "usn",
            "tax_rate": 0.06,
            "exclude_self_buyout": false
        }
    """
    try:
        if request.method == 'GET':
            # Получение настроек
            settings = db_manager.get_settings()
            return jsonify(settings)

        elif request.method == 'PATCH':
            # Обновление настроек
            data = request.get_json()

            if not data:
                return jsonify({'error': 'Нет данных для обновления'}), 400

            tax_mode = data.get('tax_mode')
            tax_rate = data.get('tax_rate')
            exclude_self_buyout = data.get('exclude_self_buyout')

            logger.info(f"Обновление настроек: tax_mode={tax_mode}, tax_rate={tax_rate}")

            success = db_manager.update_settings(
                tax_mode=tax_mode,
                tax_rate=tax_rate,
                exclude_self_buyout=exclude_self_buyout
            )

            if success:
                return jsonify({
                    'success': True,
                    'message': 'Настройки обновлены',
                    'settings': db_manager.get_settings()
                })
            else:
                return jsonify({'error': 'Не удалось обновить настройки'}), 500

    except Exception as e:
        logger.error(f"Ошибка при работе с настройками: {e}", exc_info=True)
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
