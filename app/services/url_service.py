from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.crud import get_url_by_code, update_last_accessed
from app.core.redis import redis_client, increment_hit, increment_miss


def redirect_service(db: Session, short_code: str):
    # 1. Try Redis cache first (using your optimized cache-aside logic)
    cached = redis_client.get(short_code)
    if cached:
        increment_hit()
        return (
            cached.decode("utf-8") if isinstance(cached, bytes) else cached
        )

    # 2. Cache miss: Fallback to PostgreSQL database
    increment_miss()
    url_obj = get_url_by_code(db, short_code)

    if not url_obj:
        return None

    # 3. Check expiration
    if url_obj.expires_at and url_obj.expires_at < datetime.utcnow():
        return "expired"

    # 4. Populate Redis cache for future requests
    redis_client.set(short_code, url_obj.original_url)

    # 5. Update last accessed metadata (optional/background)
    update_last_accessed(db, url_obj)

    return url_obj.original_url