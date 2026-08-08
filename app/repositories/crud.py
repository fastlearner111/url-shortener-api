from sqlalchemy.orm import Session
from app.models.models import User, UrlMapping, AnalyticsClick
from app.core.security import hash_password, verify_password
from datetime import datetime


# User CRUD

def create_user(db: Session, email: str, password: str):
    hashed = hash_password(password)
    user = User(email=email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# URL CRUD

def create_url(db: Session, original_url: str, short_code: str, owner_id: int, expires_at=None):
    url = UrlMapping(
        original_url=original_url,
        short_code=short_code,
        owner_id=owner_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        expires_at=expires_at,
    )
    db.add(url)
    db.commit()
    db.refresh(url)
    return url


def get_url_by_code(db: Session, short_code: str):
    return db.query(UrlMapping).filter(UrlMapping.short_code == short_code).first()


def update_last_accessed(db: Session, url_obj):
    url_obj.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(url_obj)
    return url_obj


# Analytics CRUD

def record_click(db: Session, url_id: int, user_agent: str, ip_address: str):
    click = AnalyticsClick(
        url_id=url_id,
        user_agent=user_agent,
        ip_address=ip_address,
        timestamp=datetime.utcnow()
    )
    db.add(click)
    db.commit()
    db.refresh(click)
    return click


def get_clicks_for_url(db: Session, url_id: int):
    return db.query(AnalyticsClick).filter(AnalyticsClick.url_id == url_id).all()