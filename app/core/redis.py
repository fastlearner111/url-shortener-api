import redis

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)

def increment_hit():
    redis_client.incr("cache_hits")

def increment_miss():
    redis_client.incr("cache_misses")
