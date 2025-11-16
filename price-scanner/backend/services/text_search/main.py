from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from rapidfuzz import fuzz, process
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Text Search Service")


class TextSearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None


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
    relevance_score: Optional[float] = None


class SearchResponse(BaseModel):
    query: str
    results: List[ProductResult]
    total_results: int
    search_type: str = "text"


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "text-search"}


@app.post("/search", response_model=SearchResponse)
async def search_by_text(request: TextSearchRequest):
    """
    Поиск товаров по тексту с нечетким совпадением (fuzzy matching)

    Алгоритм:
    1. Нормализовать поисковый запрос
    2. Применить fuzzy matching к названиям товаров
    3. Фильтровать по категории и ценовому диапазону
    4. Сортировать по релевантности
    5. Вернуть результаты
    """
    try:
        if not request.query or len(request.query.strip()) < 2:
            raise HTTPException(
                status_code=400,
                detail="Query must be at least 2 characters"
            )

        # Normalize query
        normalized_query = normalize_query(request.query)
        logger.info(f"Searching for: {normalized_query}")

        # Search marketplaces
        results = await search_marketplaces_text(
            normalized_query,
            request.category,
            request.min_price,
            request.max_price
        )

        # Apply fuzzy matching and score
        scored_results = score_results(normalized_query, results)

        # Sort by relevance
        sorted_results = sorted(
            scored_results,
            key=lambda x: x.relevance_score if x.relevance_score else 0,
            reverse=True
        )

        return SearchResponse(
            query=request.query,
            results=sorted_results,
            total_results=len(sorted_results),
            search_type="text"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def normalize_query(query: str) -> str:
    """
    Normalize search query
    """
    # Convert to lowercase
    query = query.lower().strip()

    # Remove extra spaces
    query = " ".join(query.split())

    return query


def score_results(query: str, results: List[ProductResult]) -> List[ProductResult]:
    """
    Score results using fuzzy matching
    """
    for result in results:
        # Calculate similarity score using token sort ratio
        score = fuzz.token_sort_ratio(query, result.name.lower())
        result.relevance_score = score / 100.0  # Normalize to 0-1

    return results


async def search_marketplaces_text(
    query: str,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
) -> List[ProductResult]:
    """
    Search all marketplace connectors with text query
    """
    # Mock results for MVP
    # In production, this would call the marketplace connectors service

    mock_results = [
        ProductResult(
            name=f"{query.title()} - Premium Edition",
            description="High quality premium product",
            image_url="https://via.placeholder.com/300",
            marketplace="Amazon",
            price=129.99,
            currency="USD",
            url="https://amazon.com/sample",
            rating=4.7,
            reviews_count=2345,
            in_stock=True
        ),
        ProductResult(
            name=f"{query.title()} - Standard",
            description="Great value product",
            image_url="https://via.placeholder.com/300",
            marketplace="eBay",
            price=79.99,
            currency="USD",
            url="https://ebay.com/sample",
            rating=4.2,
            reviews_count=876,
            in_stock=True
        ),
        ProductResult(
            name=f"{query.title()} - Budget",
            description="Affordable option",
            image_url="https://via.placeholder.com/300",
            marketplace="AliExpress",
            price=39.99,
            currency="USD",
            url="https://aliexpress.com/sample",
            rating=4.0,
            reviews_count=432,
            in_stock=True
        ),
    ]

    # Filter by price if specified
    if min_price is not None:
        mock_results = [r for r in mock_results if r.price >= min_price]
    if max_price is not None:
        mock_results = [r for r in mock_results if r.price <= max_price]

    return mock_results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
