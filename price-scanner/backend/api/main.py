from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from typing import List, Optional
from pydantic import BaseModel, HttpUrl
import logging

from utils.config import get_settings
from utils.redis_client import redis_client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Price-Scanner API",
    description="API Gateway для поиска и сравнения цен на маркетплейсах",
    version="1.0.0",
)

# CORS
origins = settings.ALLOWED_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
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
    search_type: str


class ImageSearchRequest(BaseModel):
    image_url: Optional[str] = None
    image_base64: Optional[str] = None


class TextSearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None


class URLSearchRequest(BaseModel):
    url: HttpUrl


# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Price-Scanner API Gateway",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Image Search
@app.post("/api/search/image", response_model=SearchResponse)
async def search_by_image(request: ImageSearchRequest):
    """
    Поиск товаров по фото
    """
    try:
        # Check cache first
        cache_key = f"image_search:{request.image_url or 'base64'}"
        cached_result = redis_client.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for image search: {cache_key}")
            return cached_result

        # Call Image Search Service
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.IMAGE_SEARCH_SERVICE_URL}/search",
                json=request.dict()
            )
            response.raise_for_status()
            result = response.json()

        # Cache the result
        redis_client.set(
            cache_key,
            result,
            ttl=settings.CACHE_TTL_IMAGE_SEARCH
        )

        return result

    except httpx.HTTPError as e:
        logger.error(f"Image search service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Image search service unavailable")
    except Exception as e:
        logger.error(f"Image search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Text Search
@app.post("/api/search/text", response_model=SearchResponse)
async def search_by_text(request: TextSearchRequest):
    """
    Поиск товаров по названию (с fuzzy matching)
    """
    try:
        # Check cache first
        cache_key = f"text_search:{request.query}:{request.category or 'all'}"
        cached_result = redis_client.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for text search: {cache_key}")
            return cached_result

        # Call Text Search Service
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.TEXT_SEARCH_SERVICE_URL}/search",
                json=request.dict()
            )
            response.raise_for_status()
            result = response.json()

        # Cache the result
        redis_client.set(
            cache_key,
            result,
            ttl=settings.CACHE_TTL_TEXT_SEARCH
        )

        return result

    except httpx.HTTPError as e:
        logger.error(f"Text search service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Text search service unavailable")
    except Exception as e:
        logger.error(f"Text search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# URL Search
@app.post("/api/search/url", response_model=SearchResponse)
async def search_by_url(request: URLSearchRequest):
    """
    Поиск аналогов товара по URL
    """
    try:
        # Check cache first
        cache_key = f"url_search:{request.url}"
        cached_result = redis_client.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for URL search: {cache_key}")
            return cached_result

        # Call URL Parser Service
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.URL_PARSER_SERVICE_URL}/parse",
                json={"url": str(request.url)}
            )
            response.raise_for_status()
            result = response.json()

        # Cache the result
        redis_client.set(
            cache_key,
            result,
            ttl=settings.CACHE_TTL_URL_PARSE
        )

        return result

    except httpx.HTTPError as e:
        logger.error(f"URL parser service error: {str(e)}")
        raise HTTPException(status_code=503, detail="URL parser service unavailable")
    except Exception as e:
        logger.error(f"URL search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Compare products
@app.get("/api/products/compare")
async def compare_products(product_ids: str):
    """
    Сравнить несколько товаров
    product_ids: comma-separated list of product IDs
    """
    try:
        ids = product_ids.split(",")
        # TODO: Implement comparison logic
        return {
            "products": [],
            "comparison": {}
        }
    except Exception as e:
        logger.error(f"Product comparison error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Get search history
@app.get("/api/history")
async def get_search_history(user_id: Optional[str] = None, limit: int = 10):
    """
    Получить историю поисков
    """
    try:
        # TODO: Implement from database
        return {
            "history": [],
            "total": 0
        }
    except Exception as e:
        logger.error(f"History retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
