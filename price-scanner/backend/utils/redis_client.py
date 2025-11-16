import redis
import json
from typing import Optional, Any
from .config import get_settings

settings = get_settings()


class RedisClient:
    def __init__(self):
        self.client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        value = self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis with optional TTL"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)

        if ttl:
            return self.client.setex(key, ttl, value)
        return self.client.set(key, value)

    def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        return self.client.delete(key) > 0

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return self.client.exists(key) > 0

    def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        keys = self.client.keys(pattern)
        if keys:
            return self.client.delete(*keys)
        return 0


# Global Redis client instance
redis_client = RedisClient()
