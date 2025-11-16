from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from urllib.parse import urlparse
import httpx
import re
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="URL Parser Service")


class URLParseRequest(BaseModel):
    url: str


class ProductResult(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    marketplace: str
    price: float
    currency: str = "USD"
    url: str
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    in_stock: bool = True


class SearchResponse(BaseModel):
    query: str
    results: List[ProductResult]
    total_results: int
    search_type: str = "url"
    source_product: Optional[ProductResult] = None


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "url-parser"}


@app.post("/parse", response_model=SearchResponse)
async def parse_url(request: URLParseRequest):
    """
    Парсинг товара по URL и поиск аналогов на других маркетплейсах

    Алгоритм:
    1. Определить маркетплейс по URL
    2. Спарсить информацию о товаре
    3. Извлечь название, цену, описание
    4. Найти аналоги на других площадках
    5. Вернуть результаты
    """
    try:
        # Detect marketplace
        marketplace = detect_marketplace(request.url)
        logger.info(f"Detected marketplace: {marketplace}")

        # Parse product info
        product_info = await parse_product_page(request.url, marketplace)

        # Find similar products on other marketplaces
        similar_products = await find_similar_products(product_info)

        return SearchResponse(
            query=product_info["name"],
            results=similar_products,
            total_results=len(similar_products),
            search_type="url",
            source_product=ProductResult(**product_info)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"URL parsing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def detect_marketplace(url: str) -> str:
    """
    Определить маркетплейс по URL
    """
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    marketplace_patterns = {
        "amazon": ["amazon.com", "amazon.co.uk", "amazon.de", "amazon.fr"],
        "ebay": ["ebay.com", "ebay.co.uk", "ebay.de"],
        "aliexpress": ["aliexpress.com", "aliexpress.ru"],
        "wildberries": ["wildberries.ru"],
        "ozon": ["ozon.ru"],
    }

    for marketplace, patterns in marketplace_patterns.items():
        if any(pattern in domain for pattern in patterns):
            return marketplace

    return "unknown"


async def parse_product_page(url: str, marketplace: str) -> dict:
    """
    Спарсить страницу товара

    В production версии здесь будет:
    - Selenium/Playwright для динамических страниц
    - Специфичные парсеры для каждого маркетплейса
    - Обработка антибот защиты
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()

        # Mock parsing for MVP
        # In production, use marketplace-specific parsers
        product_info = {
            "name": f"Product from {marketplace.title()}",
            "description": "Product description",
            "image_url": "https://via.placeholder.com/400",
            "marketplace": marketplace,
            "price": 99.99,
            "currency": "USD",
            "url": url,
            "rating": 4.5,
            "reviews_count": 1000,
            "in_stock": True
        }

        return product_info

    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch URL: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to fetch product page")


async def find_similar_products(product_info: dict) -> List[ProductResult]:
    """
    Найти похожие товары на других маркетплейсах
    """
    # In production, this would:
    # 1. Extract key features from product_info
    # 2. Search other marketplaces using text/image search
    # 3. Apply similarity scoring
    # 4. Return best matches

    # Mock results for MVP
    marketplaces = ["Amazon", "eBay", "AliExpress", "Walmart"]
    current_marketplace = product_info.get("marketplace", "").title()

    results = []
    for mp in marketplaces:
        if mp.lower() != current_marketplace.lower():
            results.append(ProductResult(
                name=product_info["name"],
                description=f"Similar product on {mp}",
                image_url=product_info["image_url"],
                marketplace=mp,
                price=product_info["price"] * (0.8 + len(mp) * 0.05),
                currency="USD",
                url=f"https://{mp.lower()}.com/sample",
                rating=4.0 + (len(mp) % 5) * 0.1,
                reviews_count=500 + len(mp) * 100,
                in_stock=True
            ))

    return results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
