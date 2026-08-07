import redis
from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def increment_hit():
    redis_client.incr("cache_hits")

def increment_miss():
    redis_client.incr("cache_misses")
