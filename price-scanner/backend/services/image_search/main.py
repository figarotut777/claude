from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import httpx
import base64
import io
import logging
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Image Search Service")


class ImageSearchRequest(BaseModel):
    image_url: Optional[str] = None
    image_base64: Optional[str] = None


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
    search_type: str = "image"


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "image-search"}


@app.post("/search", response_model=SearchResponse)
async def search_by_image(request: ImageSearchRequest):
    """
    Поиск товаров по изображению используя Google Vision API

    Алгоритм:
    1. Получить изображение (URL или base64)
    2. Использовать Vision API для распознавания объектов
    3. Извлечь ключевые слова и категории
    4. Отправить запросы к маркетплейс-коннекторам
    5. Агрегировать и нормализовать результаты
    """
    try:
        # Validate input
        if not request.image_url and not request.image_base64:
            raise HTTPException(
                status_code=400,
                detail="Either image_url or image_base64 must be provided"
            )

        # Load image
        image_data = None
        if request.image_url:
            async with httpx.AsyncClient() as client:
                response = await client.get(request.image_url)
                response.raise_for_status()
                image_data = response.content
        elif request.image_base64:
            image_data = base64.b64decode(request.image_base64)

        # Validate image
        try:
            img = Image.open(io.BytesIO(image_data))
            img.verify()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")

        # TODO: Integrate with Google Vision API
        # For MVP, we'll use a mock implementation
        detected_labels = await detect_labels_mock(image_data)

        logger.info(f"Detected labels: {detected_labels}")

        # Search marketplaces with detected keywords
        results = await search_marketplaces(detected_labels)

        return SearchResponse(
            query=", ".join(detected_labels[:3]),
            results=results,
            total_results=len(results),
            search_type="image"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def detect_labels_mock(image_data: bytes) -> List[str]:
    """
    Mock implementation of image label detection
    In production, this would use Google Vision API
    """
    # This is a placeholder - in real implementation, you would:
    # 1. Send image to Google Vision API
    # 2. Get web entities, labels, and text detection
    # 3. Extract product-related keywords

    return ["Product", "Electronics", "Device"]


async def search_marketplaces(keywords: List[str]) -> List[ProductResult]:
    """
    Search all marketplace connectors with extracted keywords
    """
    # Mock results for MVP
    # In production, this would call the marketplace connectors service

    mock_results = [
        ProductResult(
            name=f"Sample Product - {keywords[0]}",
            description="High quality product",
            image_url="https://via.placeholder.com/300",
            marketplace="Amazon",
            price=99.99,
            currency="USD",
            url="https://amazon.com/sample",
            rating=4.5,
            reviews_count=1234,
            in_stock=True
        ),
        ProductResult(
            name=f"Alternative {keywords[0]}",
            description="Great alternative",
            image_url="https://via.placeholder.com/300",
            marketplace="eBay",
            price=89.99,
            currency="USD",
            url="https://ebay.com/sample",
            rating=4.3,
            reviews_count=567,
            in_stock=True
        ),
    ]

    return mock_results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
