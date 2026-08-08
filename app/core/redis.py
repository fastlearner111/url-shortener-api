import redis, os
from app.core.config import settings

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL)

def increment_hit():
    redis_client.incr("cache_hits")

def increment_miss():
    redis_client.incr("cache_misses")
