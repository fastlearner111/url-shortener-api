from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.schemas.schemas import UrlCreate, UrlResponse, UrlAnalyticsResponse
from app.services.url_service import (
    create_user_url,
    get_url_analytics,
    update_url_service,
    delete_url_service,
)

router = APIRouter(tags=["URLs"])


@router.post("/urls/shorten", response_model=UrlResponse, status_code=status.HTTP_200_OK)
def shorten_url(
    payload: UrlCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_user_url(db=db, url_in=payload, current_user_id=current_user.id)


@router.put("/urls/{short_code}", response_model=UrlResponse)
def update_url(
    short_code: str,
    payload: UrlCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_url_service(
        db=db,
        short_code=short_code,
        new_original_url=str(payload.original_url),
        current_user_id=current_user.id,
    )


@router.delete("/urls/{short_code}")
def delete_url(
    short_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_url_service(db=db, short_code=short_code, current_user_id=current_user.id)


@router.get("/urls/stats/{short_code}", response_model=UrlAnalyticsResponse)
def get_url_stats(short_code: str, db: Session = Depends(get_db)):
    url = get_url_analytics(db=db, short_code=short_code)
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    return {
        "original_url": url.original_url,
        "short_code": url.short_code,
        "created_at": url.created_at,
        "expires_at": url.expires_at,
        "total_clicks": len(url.clicks),
    }