from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import httpx
import logging
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Marketplace Connectors Service")


class SearchRequest(BaseModel):
    query: str
    marketplace: Optional[str] = None  # If None, search all
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


class SearchResponse(BaseModel):
    results: List[ProductResult]
    total_results: int
    marketplaces_searched: List[str]


# Abstract Marketplace Connector
class MarketplaceConnector(ABC):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    @abstractmethod
    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[ProductResult]:
        pass


# Amazon Connector
class AmazonConnector(MarketplaceConnector):
    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[ProductResult]:
        """
        Amazon Product Advertising API integration
        Requires API credentials
        """
        # Mock implementation for MVP
        # In production: Use Amazon Product Advertising API
        logger.info(f"Searching Amazon for: {query}")

        mock_results = [
            ProductResult(
                name=f"{query} - Amazon Choice",
                description="Amazon's choice for this product",
                image_url="https://via.placeholder.com/300",
                marketplace="Amazon",
                price=99.99,
                currency="USD",
                url="https://amazon.com/sample",
                rating=4.6,
                reviews_count=2500,
                in_stock=True
            )
        ]

        return mock_results


# eBay Connector
class EbayConnector(MarketplaceConnector):
    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[ProductResult]:
        """
        eBay Finding API integration
        """
        logger.info(f"Searching eBay for: {query}")

        # Mock implementation for MVP
        mock_results = [
            ProductResult(
                name=f"{query} - eBay Listing",
                description="Great condition, fast shipping",
                image_url="https://via.placeholder.com/300",
                marketplace="eBay",
                price=89.99,
                currency="USD",
                url="https://ebay.com/sample",
                rating=4.4,
                reviews_count=1200,
                in_stock=True
            )
        ]

        return mock_results


# AliExpress Connector
class AliExpressConnector(MarketplaceConnector):
    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[ProductResult]:
        """
        AliExpress API / Web Scraping integration
        """
        logger.info(f"Searching AliExpress for: {query}")

        # Mock implementation for MVP
        mock_results = [
            ProductResult(
                name=f"{query} - AliExpress",
                description="Free shipping, wholesale price",
                image_url="https://via.placeholder.com/300",
                marketplace="AliExpress",
                price=39.99,
                currency="USD",
                url="https://aliexpress.com/sample",
                rating=4.2,
                reviews_count=890,
                in_stock=True
            )
        ]

        return mock_results


# Wildberries Connector (Russian marketplace)
class WildberriesConnector(MarketplaceConnector):
    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[ProductResult]:
        """
        Wildberries web scraping integration
        """
        logger.info(f"Searching Wildberries for: {query}")

        mock_results = [
            ProductResult(
                name=f"{query} - Wildberries",
                description="Быстрая доставка по России",
                image_url="https://via.placeholder.com/300",
                marketplace="Wildberries",
                price=59.99,
                currency="USD",
                url="https://wildberries.ru/sample",
                rating=4.3,
                reviews_count=650,
                in_stock=True
            )
        ]

        return mock_results


# Ozon Connector (Russian marketplace)
class OzonConnector(MarketplaceConnector):
    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[ProductResult]:
        """
        Ozon API / web scraping integration
        """
        logger.info(f"Searching Ozon for: {query}")

        mock_results = [
            ProductResult(
                name=f"{query} - Ozon",
                description="Ozon premium delivery",
                image_url="https://via.placeholder.com/300",
                marketplace="Ozon",
                price=69.99,
                currency="USD",
                url="https://ozon.ru/sample",
                rating=4.5,
                reviews_count=780,
                in_stock=True
            )
        ]

        return mock_results


# Connector Registry
CONNECTORS: Dict[str, MarketplaceConnector] = {
    "amazon": AmazonConnector(),
    "ebay": EbayConnector(),
    "aliexpress": AliExpressConnector(),
    "wildberries": WildberriesConnector(),
    "ozon": OzonConnector(),
}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "marketplace-connectors"}


@app.get("/marketplaces")
async def list_marketplaces():
    """
    Список доступных маркетплейсов
    """
    return {
        "marketplaces": list(CONNECTORS.keys()),
        "total": len(CONNECTORS)
    }


@app.post("/search", response_model=SearchResponse)
async def search_marketplaces(request: SearchRequest):
    """
    Поиск товаров на маркетплейсах

    Если marketplace не указан, ищем на всех доступных
    """
    try:
        results = []
        searched_marketplaces = []

        if request.marketplace:
            # Search specific marketplace
            if request.marketplace not in CONNECTORS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unknown marketplace: {request.marketplace}"
                )

            connector = CONNECTORS[request.marketplace]
            marketplace_results = await connector.search(
                request.query,
                request.category,
                request.min_price,
                request.max_price
            )
            results.extend(marketplace_results)
            searched_marketplaces.append(request.marketplace)

        else:
            # Search all marketplaces
            for marketplace_name, connector in CONNECTORS.items():
                try:
                    marketplace_results = await connector.search(
                        request.query,
                        request.category,
                        request.min_price,
                        request.max_price
                    )
                    results.extend(marketplace_results)
                    searched_marketplaces.append(marketplace_name)
                except Exception as e:
                    logger.error(f"Error searching {marketplace_name}: {str(e)}")
                    continue

        # Apply price filters
        if request.min_price is not None:
            results = [r for r in results if r.price >= request.min_price]
        if request.max_price is not None:
            results = [r for r in results if r.price <= request.max_price]

        # Sort by price
        results.sort(key=lambda x: x.price)

        return SearchResponse(
            results=results,
            total_results=len(results),
            marketplaces_searched=searched_marketplaces
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Marketplace search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
