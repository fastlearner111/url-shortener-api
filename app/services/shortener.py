from datetime import datetime
import string
import random
from sqlalchemy.orm import Session
from app.schemas.schemas import UrlCreate
from app.models.models import UrlMapping
from app.repositories.crud import get_url_by_code

BASE62 = string.ascii_letters + string.digits

def generate_code(length: int = 7) -> str:
    return ''.join(random.choice(BASE62) for _ in range(length))


def generate_unique_code(db: Session, length: int = 7) -> str:
    code = generate_code(length)
    while get_url_by_code(db, code) is not None:
        code = generate_code(length)
    return code


def create_short_url_service(db: Session, data: UrlCreate, owner_id: int = 1):
    """Generates a unique short code, creates the database record, and returns it."""
    short_code = generate_unique_code(db)
    
    db_url = UrlMapping(
        original_url=str(data.original_url),
        short_code=short_code,
        owner_id=owner_id,
        expires_at=data.expires_at  
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url


def redirect_service(db: Session, code: str):
    """Looks up the short code in the database and returns the original URL or 'expired'."""
    db_url = get_url_by_code(db, code)
    if not db_url:
        return None
    
    # Check if the URL has an expiration date and if it has passed
    if db_url.expires_at and db_url.expires_at < datetime.utcnow():
        return "expired"
        
    return db_url.original_url