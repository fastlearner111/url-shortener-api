from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.redis import redis_client
from app.models.models import UrlMapping  

router = APIRouter(tags=["Redirect"])  

@router.get("/{code}")
def redirect_to_url(code: str, db: Session = Depends(get_db)):
    cached_url = redis_client.get(code)
    if cached_url:
        redis_client.incr("cache_hits")
        return RedirectResponse(url=cached_url, status_code=307)
    
    redis_client.incr("cache_misses")
    
    # Updated to use UrlMapping and original_url from your models.py screenshot
    db_url = db.query(UrlMapping).filter(UrlMapping.short_code == code).first()
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    redis_client.set(code, db_url.original_url)
    return RedirectResponse(url=db_url.original_url, status_code=307)