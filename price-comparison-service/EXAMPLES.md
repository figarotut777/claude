# Примеры использования API

## Запуск сервера

```bash
# Активировать виртуальное окружение
source venv/bin/activate

# Запустить сервер
uvicorn app.main:app --reload

# Сервер будет доступен на http://localhost:8000
```

## Примеры запросов

### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Ответ:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "marketplaces": ["wildberries", "ozon", "yandex_market"]
}
```

### 2. Поиск по текстовому запросу

```bash
curl -X POST http://localhost:8000/api/search/by-text \
  -H "Content-Type: application/json" \
  -d '{
    "query": "кожаная сумка Feruni",
    "max_results_per_marketplace": 10
  }'
```

**Или с Python:**
```python
import httpx
import asyncio

async def search_by_text():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/search/by-text",
            json={
                "query": "кожаная сумка Feruni",
                "max_results_per_marketplace": 10
            }
        )
        return response.json()

result = asyncio.run(search_by_text())
print(result)
```

**Ожидаемый ответ:**
```json
{
  "query": "кожаная сумка Feruni",
  "matches": [
    {
      "match_id": "match_abc123",
      "products": [
        {
          "id": "wb_12345678",
          "marketplace": "wildberries",
          "name": "Сумка кожаная женская Feruni FRN-2024-BLK",
          "brand": "Feruni",
          "model": "FRN-2024-BLK",
          "price": "4999.00",
          "currency": "RUB",
          "url": "https://www.wildberries.ru/catalog/12345678/detail.aspx"
        },
        {
          "id": "ozon_234567890",
          "marketplace": "ozon",
          "name": "Сумка женская Feruni из натуральной кожи FRN-2024-BLK",
          "brand": "Feruni",
          "model": "FRN-2024-BLK",
          "price": "5299.00",
          "currency": "RUB",
          "url": "https://www.ozon.ru/product/sumka-feruni-234567890/"
        }
      ],
      "confidence": 0.95,
      "matching_method": "brand_model",
      "cheapest_offer": {
        "marketplace": "wildberries",
        "price": "4999.00"
      },
      "price_difference": "300.00",
      "price_difference_percent": 5.66
    }
  ],
  "total_products": 6,
  "total_unique_products": 1,
  "cheapest_overall": {
    "marketplace": "wildberries",
    "price": "4999.00"
  },
  "price_range": ["4799.00", "6199.00"],
  "marketplaces_searched": ["wildberries", "ozon", "yandex_market"],
  "search_time_ms": 125.5
}
```

### 3. Поиск по URL товара

```bash
# Wildberries URL
curl -X POST http://localhost:8000/api/search/by-url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.wildberries.ru/catalog/12345678/detail.aspx",
    "max_results_per_marketplace": 10
  }'

# Ozon URL
curl -X POST http://localhost:8000/api/search/by-url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.ozon.ru/product/sumka-feruni-234567890/",
    "max_results_per_marketplace": 10
  }'

# Yandex Market URL
curl -X POST http://localhost:8000/api/search/by-url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://market.yandex.ru/product--sumka-feruni/345678901234",
    "max_results_per_marketplace": 10
  }'
```

### 4. Получить список активных маркетплейсов

```bash
curl http://localhost:8000/api/marketplaces
```

**Ответ:**
```json
{
  "marketplaces": ["wildberries", "ozon", "yandex_market"],
  "count": 3
}
```

## Интеграция в веб-приложение (JavaScript)

### Vanilla JavaScript

```javascript
async function searchProducts(query) {
  const response = await fetch('http://localhost:8000/api/search/by-text', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      max_results_per_marketplace: 10
    })
  });

  const data = await response.json();
  return data;
}

// Использование
searchProducts('кожаная сумка Feruni')
  .then(result => {
    console.log('Найдено товаров:', result.total_products);
    console.log('Самая дешёвая цена:', result.cheapest_overall?.price);

    // Отобразить результаты
    result.matches.forEach(match => {
      console.log(`\nГруппа товаров (confidence: ${match.confidence}):`);
      match.products.forEach(product => {
        console.log(`- ${product.marketplace}: ${product.price} ${product.currency}`);
      });
    });
  });
```

### React Hook

```jsx
import { useState } from 'react';

function usePriceComparison() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const searchByText = async (query) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/search/by-text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, max_results_per_marketplace: 10 })
      });

      if (!response.ok) throw new Error('Search failed');

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { searchByText, loading, result, error };
}

// Использование в компоненте
function SearchComponent() {
  const { searchByText, loading, result, error } = usePriceComparison();

  return (
    <div>
      <button onClick={() => searchByText('кожаная сумка Feruni')}>
        Поиск
      </button>

      {loading && <p>Загрузка...</p>}
      {error && <p>Ошибка: {error}</p>}

      {result && (
        <div>
          <h3>Найдено: {result.total_products} товаров</h3>
          <p>Самая низкая цена: {result.cheapest_overall?.price} ₽</p>
        </div>
      )}
    </div>
  );
}
```

## Интеграция с Python приложением

```python
import httpx
import asyncio
from typing import Optional

class PriceComparisonClient:
    """Клиент для работы с Price Comparison API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    async def search_by_text(
        self,
        query: str,
        max_results: int = 10
    ) -> dict:
        """Поиск по текстовому запросу"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/search/by-text",
                json={
                    "query": query,
                    "max_results_per_marketplace": max_results
                }
            )
            response.raise_for_status()
            return response.json()

    async def search_by_url(
        self,
        url: str,
        max_results: int = 10
    ) -> dict:
        """Поиск по URL товара"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/search/by-url",
                json={
                    "url": url,
                    "max_results_per_marketplace": max_results
                }
            )
            response.raise_for_status()
            return response.json()

    async def get_marketplaces(self) -> dict:
        """Получить список активных маркетплейсов"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/marketplaces"
            )
            response.raise_for_status()
            return response.json()

# Пример использования
async def main():
    client = PriceComparisonClient()

    # Поиск по запросу
    result = await client.search_by_text("кожаная сумка Feruni")

    print(f"Найдено {result['total_products']} товаров")
    print(f"Уникальных товаров: {result['total_unique_products']}")

    if result['cheapest_overall']:
        cheapest = result['cheapest_overall']
        print(f"\nСамое дешёвое предложение:")
        print(f"  Маркетплейс: {cheapest['marketplace']}")
        print(f"  Цена: {cheapest['price']} {cheapest['currency']}")
        print(f"  URL: {cheapest['url']}")

    # Группы совпадающих товаров
    for match in result['matches']:
        print(f"\n--- Группа товаров (уверенность: {match['confidence']}) ---")
        print(f"Метод сопоставления: {match['matching_method']}")
        print(f"Разница в цене: {match['price_difference']} ({match['price_difference_percent']:.1f}%)")

        for product in match['products']:
            print(f"  • {product['marketplace']}: {product['price']} ₽")

if __name__ == "__main__":
    asyncio.run(main())
```

## Тестирование через Swagger UI

1. Откройте http://localhost:8000/docs
2. Найдите endpoint `/api/search/by-text`
3. Нажмите "Try it out"
4. Введите данные:
   ```json
   {
     "query": "кожаная сумка Feruni",
     "max_results_per_marketplace": 10
   }
   ```
5. Нажмите "Execute"
6. Просмотрите результат

## Обработка ошибок

```python
import httpx

async def safe_search(query: str):
    """Безопасный поиск с обработкой ошибок"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8000/api/search/by-text",
                json={"query": query, "max_results_per_marketplace": 10}
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                print("Ошибка валидации запроса")
            elif response.status_code == 404:
                print("Товары не найдены")
            elif response.status_code == 500:
                print("Внутренняя ошибка сервера")
            else:
                print(f"Неожиданная ошибка: {response.status_code}")

    except httpx.TimeoutException:
        print("Превышено время ожидания")
    except httpx.ConnectError:
        print("Не удалось подключиться к серверу")
    except Exception as e:
        print(f"Ошибка: {e}")

    return None

# Использование
result = await safe_search("кожаная сумка Feruni")
if result:
    print(f"Успешно! Найдено {result['total_products']} товаров")
```

## Производительность

Для улучшения производительности при множественных запросах:

```python
import asyncio
import httpx

async def batch_search(queries: list[str]):
    """Параллельный поиск по нескольким запросам"""
    async with httpx.AsyncClient() as client:
        tasks = [
            client.post(
                "http://localhost:8000/api/search/by-text",
                json={"query": query, "max_results_per_marketplace": 10}
            )
            for query in queries
        ]

        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses if r.status_code == 200]

# Пример
queries = [
    "кожаная сумка Feruni",
    "телефон Samsung",
    "ноутбук Apple"
]

results = await batch_search(queries)
for i, result in enumerate(results):
    print(f"\nЗапрос {i+1}: {result['query']}")
    print(f"Найдено: {result['total_products']} товаров")
```
