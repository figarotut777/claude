from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import re
import logging
from slugify import slugify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Product Normalizer Service")


class ProductData(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    currency: str = "USD"
    marketplace: str
    category: Optional[str] = None
    brand: Optional[str] = None


class NormalizedProduct(BaseModel):
    original_name: str
    normalized_name: str
    slug: str
    description: Optional[str] = None
    price: float
    currency: str
    marketplace: str
    category: Optional[str] = None
    brand: Optional[str] = None
    extracted_features: dict


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "normalizer"}


@app.post("/normalize", response_model=NormalizedProduct)
async def normalize_product(product: ProductData):
    """
    Нормализация данных о товаре

    Выполняет:
    1. Очистку названия от мусора
    2. Извлечение бренда
    3. Извлечение характеристик
    4. Создание slug для URL
    5. Категоризацию
    """
    try:
        # Normalize name
        normalized_name = normalize_product_name(product.name)

        # Extract brand if not provided
        brand = product.brand or extract_brand(product.name)

        # Create slug
        slug = slugify(normalized_name)

        # Extract features from name and description
        features = extract_features(product.name, product.description)

        # Determine category if not provided
        category = product.category or categorize_product(
            normalized_name,
            product.description
        )

        return NormalizedProduct(
            original_name=product.name,
            normalized_name=normalized_name,
            slug=slug,
            description=product.description,
            price=product.price,
            currency=product.currency,
            marketplace=product.marketplace,
            category=category,
            brand=brand,
            extracted_features=features
        )

    except Exception as e:
        logger.error(f"Normalization error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/normalize_batch", response_model=List[NormalizedProduct])
async def normalize_products_batch(products: List[ProductData]):
    """
    Пакетная нормализация товаров
    """
    try:
        normalized = []
        for product in products:
            result = await normalize_product(product)
            normalized.append(result)

        return normalized

    except Exception as e:
        logger.error(f"Batch normalization error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def normalize_product_name(name: str) -> str:
    """
    Очистка и нормализация названия товара
    """
    # Remove extra whitespace
    name = " ".join(name.split())

    # Remove common marketplace junk
    junk_patterns = [
        r'\[.*?\]',  # Remove brackets
        r'\(.*?\)',  # Remove parentheses
        r'NEW\s*!?',  # Remove "NEW"
        r'FREE\s+SHIPPING',  # Remove "FREE SHIPPING"
        r'SALE\s*!?',  # Remove "SALE"
        r'\d+%\s*OFF',  # Remove percentage off
    ]

    for pattern in junk_patterns:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)

    # Remove extra whitespace again
    name = " ".join(name.split())

    return name.strip()


def extract_brand(name: str) -> Optional[str]:
    """
    Попытка извлечь бренд из названия
    """
    # Common brand patterns
    # Usually brands are at the start of product names

    # List of known brands (in production, use a comprehensive database)
    known_brands = [
        "Apple", "Samsung", "Sony", "LG", "Nike", "Adidas",
        "Dell", "HP", "Lenovo", "ASUS", "Acer"
    ]

    words = name.split()
    if words:
        first_word = words[0]
        for brand in known_brands:
            if brand.lower() == first_word.lower():
                return brand

    return None


def extract_features(name: str, description: Optional[str]) -> dict:
    """
    Извлечение характеристик из названия и описания
    """
    features = {}

    # Extract color
    colors = ["black", "white", "red", "blue", "green", "yellow", "silver", "gold"]
    for color in colors:
        if re.search(rf'\b{color}\b', name, re.IGNORECASE):
            features["color"] = color.capitalize()
            break

    # Extract size (clothing)
    sizes = ["XS", "S", "M", "L", "XL", "XXL"]
    for size in sizes:
        if re.search(rf'\b{size}\b', name, re.IGNORECASE):
            features["size"] = size
            break

    # Extract capacity (electronics)
    capacity_match = re.search(r'(\d+)\s*(GB|TB|MB)', name, re.IGNORECASE)
    if capacity_match:
        features["storage"] = capacity_match.group(0)

    # Extract screen size (electronics)
    screen_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:inch|")', name, re.IGNORECASE)
    if screen_match:
        features["screen_size"] = f"{screen_match.group(1)} inch"

    return features


def categorize_product(name: str, description: Optional[str]) -> str:
    """
    Автоматическая категоризация товара
    """
    name_lower = name.lower()
    desc_lower = (description or "").lower()

    # Category keywords
    categories = {
        "Electronics": ["phone", "laptop", "computer", "tablet", "headphones", "camera"],
        "Clothing": ["shirt", "pants", "dress", "shoes", "jacket", "sneakers"],
        "Home & Garden": ["furniture", "lamp", "table", "chair", "sofa", "bed"],
        "Sports": ["ball", "bike", "fitness", "gym", "yoga", "running"],
        "Books": ["book", "novel", "guide", "manual"],
        "Toys": ["toy", "game", "puzzle", "doll", "action figure"],
    }

    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in name_lower or keyword in desc_lower:
                return category

    return "Other"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
