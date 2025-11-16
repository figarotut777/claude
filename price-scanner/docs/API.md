# Price-Scanner API Documentation

## Base URL

```
http://localhost:8000
```

Production:
```
https://api.price-scanner.com
```

---

## Authentication

В текущей версии MVP аутентификация не требуется. В будущих версиях будет добавлена JWT аутентификация.

---

## Endpoints

### Health Check

#### GET `/health`

Проверка работоспособности API Gateway.

**Response:**
```json
{
  "status": "healthy",
  "service": "api-gateway",
  "version": "1.0.0"
}
```

---

### Search Endpoints

#### POST `/api/search/text`

Поиск товаров по текстовому запросу.

**Request Body:**
```json
{
  "query": "iPhone 15 Pro",
  "category": "Electronics",
  "min_price": 500.0,
  "max_price": 2000.0
}
```

**Parameters:**
- `query` (string, required): Поисковый запрос
- `category` (string, optional): Категория товара
- `min_price` (number, optional): Минимальная цена
- `max_price` (number, optional): Максимальная цена

**Response:**
```json
{
  "query": "iPhone 15 Pro",
  "results": [
    {
      "name": "iPhone 15 Pro 256GB",
      "description": "Latest iPhone with titanium design",
      "image_url": "https://example.com/image.jpg",
      "marketplace": "Amazon",
      "price": 999.99,
      "currency": "USD",
      "url": "https://amazon.com/...",
      "rating": 4.7,
      "reviews_count": 1234,
      "in_stock": true,
      "relevance_score": 0.95
    }
  ],
  "total_results": 15,
  "search_type": "text"
}
```

---

#### POST `/api/search/image`

Поиск товаров по изображению.

**Request Body:**
```json
{
  "image_url": "https://example.com/product.jpg"
}
```

OR

```json
{
  "image_base64": "base64_encoded_image_data"
}
```

**Parameters:**
- `image_url` (string, optional): URL изображения
- `image_base64` (string, optional): Base64-encoded изображение

**Response:**
```json
{
  "query": "Electronics, Device",
  "results": [
    {
      "name": "Similar Product",
      "description": "Product description",
      "image_url": "https://example.com/image.jpg",
      "marketplace": "eBay",
      "price": 89.99,
      "currency": "USD",
      "url": "https://ebay.com/...",
      "rating": 4.5,
      "reviews_count": 567,
      "in_stock": true
    }
  ],
  "total_results": 10,
  "search_type": "image"
}
```

---

#### POST `/api/search/url`

Поиск аналогов товара по URL.

**Request Body:**
```json
{
  "url": "https://amazon.com/product/B08..."
}
```

**Parameters:**
- `url` (string, required): URL товара на маркетплейсе

**Response:**
```json
{
  "query": "Product Name",
  "results": [
    {
      "name": "Product Name",
      "description": "Similar product on another marketplace",
      "image_url": "https://example.com/image.jpg",
      "marketplace": "eBay",
      "price": 79.99,
      "currency": "USD",
      "url": "https://ebay.com/...",
      "rating": 4.3,
      "reviews_count": 890,
      "in_stock": true
    }
  ],
  "total_results": 8,
  "search_type": "url",
  "source_product": {
    "name": "Original Product",
    "marketplace": "Amazon",
    "price": 99.99,
    "currency": "USD",
    "url": "https://amazon.com/product/B08..."
  }
}
```

---

### Product Endpoints

#### GET `/api/products/compare`

Сравнить несколько товаров.

**Query Parameters:**
- `product_ids` (string, required): Comma-separated list of product IDs

**Example:**
```
GET /api/products/compare?product_ids=uuid1,uuid2,uuid3
```

**Response:**
```json
{
  "products": [
    {
      "id": "uuid1",
      "name": "Product 1",
      "price": 99.99,
      "marketplace": "Amazon"
    },
    {
      "id": "uuid2",
      "name": "Product 2",
      "price": 89.99,
      "marketplace": "eBay"
    }
  ],
  "comparison": {
    "lowest_price": 89.99,
    "highest_price": 99.99,
    "average_price": 94.99
  }
}
```

---

### History Endpoints

#### GET `/api/history`

Получить историю поисков.

**Query Parameters:**
- `user_id` (string, optional): ID пользователя
- `limit` (integer, optional): Количество результатов (default: 10)

**Example:**
```
GET /api/history?user_id=user123&limit=20
```

**Response:**
```json
{
  "history": [
    {
      "id": "uuid",
      "search_type": "text",
      "query": "iPhone 15",
      "results_count": 15,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 42
}
```

---

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid request parameters"
}
```

### 404 Not Found

```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

### 503 Service Unavailable

```json
{
  "detail": "Service temporarily unavailable"
}
```

---

## Rate Limiting

### Free Tier
- 10 requests per day
- Burst: 5 requests per minute

### Pro Tier
- 1000 requests per day
- Burst: 50 requests per minute

### Enterprise Tier
- Unlimited requests
- Custom rate limits

**Rate Limit Headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1642262400
```

---

## Microservices Endpoints

Для прямого доступа к микросервисам (для разработки):

### Image Search Service (Port 8001)

```
POST http://localhost:8001/search
```

### Text Search Service (Port 8002)

```
POST http://localhost:8002/search
```

### URL Parser Service (Port 8003)

```
POST http://localhost:8003/parse
```

### Marketplace Connectors (Port 8004)

```
GET http://localhost:8004/marketplaces
POST http://localhost:8004/search
```

### Normalizer Service (Port 8005)

```
POST http://localhost:8005/normalize
POST http://localhost:8005/normalize_batch
```

---

## Code Examples

### Python

```python
import requests

# Text search
response = requests.post(
    'http://localhost:8000/api/search/text',
    json={'query': 'iPhone 15 Pro'}
)
results = response.json()

# Image search
with open('product.jpg', 'rb') as f:
    image_data = f.read()
    import base64
    image_base64 = base64.b64encode(image_data).decode()

response = requests.post(
    'http://localhost:8000/api/search/image',
    json={'image_base64': image_base64}
)
results = response.json()
```

### JavaScript

```javascript
// Text search
const response = await fetch('http://localhost:8000/api/search/text', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'iPhone 15 Pro'
  })
});
const results = await response.json();

// URL search
const response = await fetch('http://localhost:8000/api/search/url', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    url: 'https://amazon.com/product/...'
  })
});
const results = await response.json();
```

### cURL

```bash
# Text search
curl -X POST http://localhost:8000/api/search/text \
  -H "Content-Type: application/json" \
  -d '{"query": "iPhone 15 Pro"}'

# URL search
curl -X POST http://localhost:8000/api/search/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://amazon.com/product/..."}'
```

---

## WebSocket Support (Future)

Планируется добавить WebSocket для real-time уведомлений:

```
ws://localhost:8000/ws/price-updates
```

---

## API Versioning

Текущая версия: **v1**

В будущем будет доступна версионность через URL:
```
https://api.price-scanner.com/v2/search/text
```

---

## Support

Для вопросов по API:
- Email: api-support@price-scanner.com
- GitHub Issues: https://github.com/yourusername/price-scanner/issues
