"""
Wildberries API client with async support and comprehensive error handling.

API Documentation:
- Official WB Suppliers API: https://openapi.wildberries.ru/
- Supplies API endpoint: https://supplies-api.wildberries.ru/
- Main endpoints used:
  * GET /api/v1/warehouses - Get list of warehouses
  * GET /api/v1/acceptance/coefficients - Get acceptance coefficients and slots
  * POST /api/v1/acceptance - Book a slot
"""
import asyncio
from datetime import datetime
from typing import Optional
import httpx
from models import Warehouse, TimeSlot, BookingRequest, LogEntry


class WildberriesAPIError(Exception):
    """Base exception for WB API errors."""
    pass


class AuthenticationError(WildberriesAPIError):
    """Authentication failed (401/403)."""
    pass


class RateLimitError(WildberriesAPIError):
    """Rate limit exceeded (429)."""
    pass


class ServerError(WildberriesAPIError):
    """Server error (5xx)."""
    pass


class WildberriesAPI:
    """
    Async client for Wildberries Supplies API.

    Handles authentication, rate limiting, and error recovery.
    """

    BASE_URL = "https://supplies-api.wildberries.ru"

    def __init__(self, token: str, timeout: float = 30.0):
        """
        Initialize the API client.

        Args:
            token: WB API authorization token
            timeout: Request timeout in seconds
        """
        self.token = token
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=self._get_headers(),
            timeout=self.timeout,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with authorization."""
        return {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> dict:
        """
        Make an API request with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for httpx request

        Returns:
            Response JSON data

        Raises:
            AuthenticationError: Invalid token or unauthorized
            RateLimitError: Rate limit exceeded
            ServerError: Server-side error
            WildberriesAPIError: Other API errors
        """
        if not self._client:
            raise RuntimeError("API client not initialized. Use 'async with' context manager.")

        try:
            response = await self._client.request(method, endpoint, **kwargs)

            # Handle different status codes
            if response.status_code == 200:
                return response.json() if response.content else {}
            elif response.status_code == 201:
                return response.json() if response.content else {"status": "created"}
            elif response.status_code == 204:
                return {"status": "success"}
            elif response.status_code in (401, 403):
                raise AuthenticationError(f"Authentication failed: {response.text}")
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After", "60")
                raise RateLimitError(f"Rate limit exceeded. Retry after {retry_after} seconds.")
            elif 500 <= response.status_code < 600:
                raise ServerError(f"Server error ({response.status_code}): {response.text}")
            else:
                raise WildberriesAPIError(
                    f"API request failed ({response.status_code}): {response.text}"
                )

        except httpx.TimeoutException:
            raise WildberriesAPIError("Request timeout")
        except httpx.NetworkError as e:
            raise WildberriesAPIError(f"Network error: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise WildberriesAPIError(f"HTTP error: {str(e)}")

    async def get_warehouses(self) -> list[Warehouse]:
        """
        Fetch list of available warehouses.

        Returns:
            List of Warehouse objects

        Example response:
        [
            {"id": 1, "name": "Коледино", "address": "г. Москва"},
            {"id": 2, "name": "Подольск", "address": "г. Подольск"}
        ]
        """
        try:
            # Endpoint: GET /api/v1/warehouses
            data = await self._request("GET", "/api/v1/warehouses")

            # Parse response into Warehouse models
            warehouses = []
            if isinstance(data, list):
                for item in data:
                    try:
                        warehouse = Warehouse(**item)
                        warehouses.append(warehouse)
                    except Exception as e:
                        print(f"Failed to parse warehouse data: {item}, error: {e}")
                        continue

            return warehouses

        except Exception as e:
            raise WildberriesAPIError(f"Failed to fetch warehouses: {str(e)}")

    async def get_available_slots(
        self,
        warehouse_id: int,
        date_from: str,
        date_to: str
    ) -> list[TimeSlot]:
        """
        Fetch available slots for a warehouse in a date range.

        Args:
            warehouse_id: Warehouse ID
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)

        Returns:
            List of TimeSlot objects

        Example response:
        [
            {
                "date": "2025-11-20",
                "time": "09:00-12:00",
                "coefficient": 1.5,
                "quota": 100
            }
        ]
        """
        try:
            # Endpoint: GET /api/v1/acceptance/coefficients
            params = {
                "warehouseID": warehouse_id,
                "dateFrom": date_from,
                "dateTo": date_to,
            }

            data = await self._request("GET", "/api/v1/acceptance/coefficients", params=params)

            # Parse response into TimeSlot models
            slots = []
            if isinstance(data, list):
                for item in data:
                    try:
                        # Add warehouse_id to the slot data
                        item["warehouse_id"] = warehouse_id
                        slot = TimeSlot(**item)
                        slots.append(slot)
                    except Exception as e:
                        print(f"Failed to parse slot data: {item}, error: {e}")
                        continue

            return slots

        except Exception as e:
            raise WildberriesAPIError(
                f"Failed to fetch slots for warehouse {warehouse_id}: {str(e)}"
            )

    async def book_slot(self, booking: BookingRequest) -> dict:
        """
        Book a delivery slot.

        Args:
            booking: BookingRequest with slot details

        Returns:
            Booking confirmation data

        Example request body:
        {
            "warehouseID": 1,
            "date": "2025-11-20",
            "time": "09:00-12:00",
            "shipmentType": "box"
        }
        """
        try:
            # Endpoint: POST /api/v1/acceptance
            payload = {
                "warehouseID": booking.warehouse_id,
                "date": booking.date,
                "time": booking.time,
                "shipmentType": booking.shipment_type,
            }

            result = await self._request("POST", "/api/v1/acceptance", json=payload)

            return {
                "success": True,
                "booking_id": result.get("id"),
                "message": "Slot booked successfully",
                "data": result,
            }

        except AuthenticationError:
            return {
                "success": False,
                "error": "Authentication failed. Check your API token.",
            }
        except RateLimitError as e:
            return {
                "success": False,
                "error": f"Rate limit exceeded: {str(e)}",
            }
        except WildberriesAPIError as e:
            return {
                "success": False,
                "error": f"Booking failed: {str(e)}",
            }

    async def test_connection(self) -> tuple[bool, str]:
        """
        Test API connection and token validity.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            warehouses = await self.get_warehouses()
            return True, f"Connection successful. Found {len(warehouses)} warehouses."
        except AuthenticationError:
            return False, "Authentication failed. Invalid API token."
        except WildberriesAPIError as e:
            return False, f"Connection failed: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"


async def example_usage():
    """Example usage of the API client."""
    token = "YOUR_WB_API_TOKEN"

    async with WildberriesAPI(token) as api:
        # Test connection
        success, message = await api.test_connection()
        print(f"Connection test: {message}")

        if success:
            # Get warehouses
            warehouses = await api.get_warehouses()
            print(f"\nFound {len(warehouses)} warehouses:")
            for wh in warehouses[:3]:
                print(f"  - {wh.name} (ID: {wh.id})")

            # Get available slots
            if warehouses:
                slots = await api.get_available_slots(
                    warehouse_id=warehouses[0].id,
                    date_from="2025-11-20",
                    date_to="2025-11-25"
                )
                print(f"\nFound {len(slots)} available slots")
                for slot in slots[:3]:
                    print(f"  - {slot.date} {slot.time}: coefficient {slot.coefficient}")


if __name__ == "__main__":
    asyncio.run(example_usage())
