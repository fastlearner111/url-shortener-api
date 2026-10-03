import logging
import os
import redis

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class SimpleRedisCache:
    def __init__(self):
        # Try to connect when the app starts
        try:
            self.client = redis.from_url(REDIS_URL, decode_responses=True)
            self.client.ping()  # Test if server is actually up
        except Exception:
            logger.warning("Redis cache unavailable at startup, running without cache")
            self.client = None  # If offline (like in tests), safely set to None

    def get(self, key: str):
        if not self.client:
            return None
        try:
            return self.client.get(key)
        except Exception:
            return None

    def set(self, key: str, value: str, ex=None):
        if not self.client:
            return None
        try:
            return self.client.set(key, value, ex=ex)
        except Exception:
            return None

    def incr(self, key: str):
        if not self.client:
            return None
        try:
            return self.client.incr(key)
        except Exception:
            return None

    def delete(self, key: str):
        if not self.client:
            return None
        try:
            return self.client.delete(key)
        except Exception:
            logger.warning("Redis delete failed for key %s, cache may be stale", key)
            return None

# Global instance you import everywhere
redis_client = SimpleRedisCache()

def increment_hit():
    redis_client.incr("cache_hits")

def increment_miss():
    redis_client.incr("cache_misses")