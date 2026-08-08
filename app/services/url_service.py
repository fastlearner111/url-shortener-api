import string
import random
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.crud import create_url, get_url_by_code, update_last_accessed
from app.core.redis import redis_client, increment_hit, increment_miss
from app.schemas.schemas import UrlCreate

def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))

def create_user_url(db: Session, url_in: UrlCreate, current_user_id: int):
    short_code = getattr(url_in, "custom_code", None)
    
    if not short_code:
        for _ in range(5):
            code = generate_short_code()
            if not get_url_by_code(db, code):
                short_code = code
                break
        else:
            short_code = generate_short_code(8)
    else:
        if get_url_by_code(db, short_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Custom short code already in use."
            )

    return create_url(
        db=db,
        original_url=url_in.original_url,
        short_code=short_code,
        owner_id=current_user_id,
        expires_at=getattr(url_in, "expires_at", None)
    )

def get_url_analytics(db: Session, short_code: str):
    url_obj = get_url_by_code(db, short_code)
    if not url_obj:
        return None
    return url_obj

def redirect_service(db: Session, short_code: str):
    cached = redis_client.get(short_code)
    if cached:
        increment_hit()
        return cached.decode("utf-8") if isinstance(cached, bytes) else cached

    increment_miss()
    url_obj = get_url_by_code(db, short_code)

    if not url_obj:
        return None

    if url_obj.expires_at and url_obj.expires_at < datetime.utcnow():
        return "expired"

    ttl = 3600
    if url_obj.expires_at:
        delta = (url_obj.expires_at - datetime.utcnow()).total_seconds()
        if delta > 0:
            ttl = int(delta)
        else:
            return "expired"

    redis_client.set(short_code, url_obj.original_url, ex=ttl)
    update_last_accessed(db, url_obj)

    return url_obj.original_url

def update_url_service(db: Session, short_code: str, new_original_url: str, current_user_id: int):
    url_obj = get_url_by_code(db, short_code)
    if not url_obj:
        raise HTTPException(status_code=404, detail="URL not found")
    if url_obj.owner_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this URL")
    
    url_obj.original_url = new_original_url
    db.commit()
    db.refresh(url_obj)

    # Bug #7 Fix: Explicit cache invalidation on update
    redis_client.delete(short_code)
    return url_obj

def delete_url_service(db: Session, short_code: str, current_user_id: int):
    url_obj = get_url_by_code(db, short_code)
    if not url_obj:
        raise HTTPException(status_code=404, detail="URL not found")
    if url_obj.owner_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this URL")

    db.delete(url_obj)
    db.commit()

    # Bug #7 Fix: Explicit cache invalidation on delete
    redis_client.delete(short_code)
    return {"detail": "URL deleted successfully"}