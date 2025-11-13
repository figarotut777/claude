"""
Главное FastAPI приложение.

Предоставляет HTTP API для сравнения цен на товары с разных маркетплейсов.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .models import (
    SearchByTextRequest,
    SearchByUrlRequest,
    ComparisonResult,
)
from .services import PriceComparisonService
from .utils import is_valid_marketplace_url


# Lifespan context manager для инициализации и очистки ресурсов
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения.
    """
    # Startup
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📊 Active marketplaces: {comparison_service.search_service.get_active_marketplaces()}")

    yield

    # Shutdown
    print("👋 Shutting down...")


# Создаём FastAPI приложение
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    API для сравнения цен на товары с российских маркетплейсов:
    - Yandex Market
    - Wildberries
    - Ozon

    Поддерживает два режима работы:
    1. Поиск по текстовому запросу (например, "кожаная сумка Feruni")
    2. Поиск по URL товара с одного маркетплейса

    Автоматически находит одинаковые товары и сравнивает цены.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware (для фронтенда)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальный экземпляр сервиса сравнения
comparison_service = PriceComparisonService()


@app.get("/", tags=["Root"])
async def root():
    """
    Корневой endpoint с информацией о сервисе.
    """
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "active_marketplaces": comparison_service.search_service.get_active_marketplaces(),
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint для мониторинга.
    """
    return {
        "status": "healthy",
        "version": settings.app_version,
        "marketplaces": comparison_service.search_service.get_active_marketplaces(),
    }


@app.post(
    "/api/search/by-text",
    response_model=ComparisonResult,
    tags=["Search"],
    summary="Поиск и сравнение по текстовому запросу",
)
async def search_by_text(request: SearchByTextRequest) -> ComparisonResult:
    """
    Поиск товаров по текстовому запросу на всех маркетплейсах и сравнение цен.

    **Пример запроса:**
    ```json
    {
        "query": "кожаная сумка Feruni",
        "max_results_per_marketplace": 10
    }
    ```

    **Как это работает:**
    1. Запрос отправляется на Yandex Market, Wildberries, Ozon
    2. Алгоритм находит одинаковые товары по:
       - Штрих-коду (GTIN)
       - Бренду и модели
       - Fuzzy matching по названию
    3. Группирует товары и сравнивает цены
    4. Возвращает результат с указанием самого дешёвого предложения

    **Результат содержит:**
    - Список групп одинаковых товаров (matches)
    - Самое дешёвое предложение (cheapest_overall)
    - Диапазон цен (price_range)
    - Время выполнения запроса
    """
    try:
        result = await comparison_service.compare_by_text(
            query=request.query,
            max_results_per_marketplace=request.max_results_per_marketplace,
        )
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при выполнении поиска: {str(e)}",
        )


@app.post(
    "/api/search/by-url",
    response_model=ComparisonResult,
    tags=["Search"],
    summary="Поиск и сравнение по URL товара",
)
async def search_by_url(request: SearchByUrlRequest) -> ComparisonResult:
    """
    Поиск того же товара на других маркетплейсах по URL.

    **Пример запроса:**
    ```json
    {
        "url": "https://www.wildberries.ru/catalog/12345678/detail.aspx",
        "max_results_per_marketplace": 10
    }
    ```

    **Как это работает:**
    1. Парсим URL и извлекаем метаданные товара:
       - Название
       - Бренд
       - Модель
       - Штрих-код (GTIN)
       - Артикул
       - Характеристики
    2. Ищем этот же товар на других маркетплейсах используя извлечённые данные
    3. Сопоставляем товары и сравниваем цены
    4. Возвращаем результат

    **Поддерживаемые маркетплейсы:**
    - Wildberries: https://www.wildberries.ru/catalog/{ID}/detail.aspx
    - Ozon: https://www.ozon.ru/product/{slug}-{ID}/
    - Yandex Market: https://market.yandex.ru/product--{slug}/{ID}
    """
    # Валидация URL
    if not is_valid_marketplace_url(request.url):
        raise HTTPException(
            status_code=400,
            detail="Неверный URL маркетплейса. Поддерживаются: Wildberries, Ozon, Yandex Market",
        )

    try:
        result = await comparison_service.compare_by_url(
            url=request.url,
            max_results_per_marketplace=request.max_results_per_marketplace,
        )

        # Если парсинг URL не удался
        if result.total_products == 0 and not result.matches:
            raise HTTPException(
                status_code=404,
                detail="Не удалось распарсить товар по указанному URL или товар не найден на других площадках",
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при выполнении поиска: {str(e)}",
        )


@app.get("/api/marketplaces", tags=["Info"])
async def get_active_marketplaces():
    """
    Получить список активных маркетплейсов.

    Возвращает маркетплейсы, которые включены в конфигурации.
    """
    return {
        "marketplaces": comparison_service.search_service.get_active_marketplaces(),
        "count": len(comparison_service.search_service.get_active_marketplaces()),
    }


# Запуск приложения
# Использование: uvicorn app.main:app --reload
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
