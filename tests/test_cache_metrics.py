from unittest.mock import patch
from app.core.redis import increment_hit, increment_miss

@patch("app.core.redis.redis_client")
def test_increment_hit(mock_redis_client):
    # Call the helper function
    increment_hit()
    
    # Assert that Redis was told to increment "cache_hits"
    mock_redis_client.incr.assert_called_once_with("cache_hits")

@patch("app.core.redis.redis_client")
def test_increment_miss(mock_redis_client):
    # Call the helper function
    increment_miss()
    
    # Assert that Redis was told to increment "cache_misses"
    mock_redis_client.incr.assert_called_once_with("cache_misses")