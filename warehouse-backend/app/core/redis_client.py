import redis
import json
from typing import Optional, Any
from app.core.config import settings

class RedisClient:
    def __init__(self):
        self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    def get(self, key: str) -> Optional[Any]:
        data = self.client.get(key)
        if data:
            return json.loads(data)
        return None

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        self.client.setex(key, ttl, json.dumps(value))

    def delete(self, key: str) -> None:
        self.client.delete(key)

    def delete_pattern(self, pattern: str) -> None:
        for key in self.client.scan_iter(pattern):
            self.client.delete(key)

redis_client = RedisClient()