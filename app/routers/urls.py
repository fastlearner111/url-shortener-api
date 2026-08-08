from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.schemas.schemas import UrlCreate, UrlResponse, UrlAnalyticsResponse
from app.services.url_service import (
    create_user_url,
    get_url_analytics,
    redirect_service,
    update_url_service,
    delete_url_service,
)

router = APIRouter(tags=["URLs"])

@router.post("/urls/shorten", response_model=UrlResponse, status_code=status.HTTP_200_OK)
def shorten_url(
    payload: UrlCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Bug #9 Fix: Secure JWT auth active
):
    return create_user_url(db=db, url_in=payload, current_user_id=current_user.id)

@router.put("/urls/{short_code}", response_model=UrlResponse)
def update_url(
    short_code: str,
    payload: UrlCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_url_service(db=db, short_code=short_code, new_original_url=str(payload.original_url), current_user_id=current_user.id)

@router.delete("/urls/{short_code}")
def delete_url(
    short_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return delete_url_service(db=db, short_code=short_code, current_user_id=current_user.id)

@router.get("/urls/stats/{short_code}", response_model=UrlAnalyticsResponse)
def get_url_stats(short_code: str, db: Session = Depends(get_db)):
    analytics = get_url_analytics(db=db, short_code=short_code)
    if not analytics:
        raise HTTPException(status_code=404, detail="URL not found")
    
    raw_clicks = getattr(analytics, "clicks", getattr(analytics, "total_clicks", 0))
    if isinstance(raw_clicks, list):
        total_clicks = len(raw_clicks)
    elif isinstance(raw_clicks, int):
        total_clicks = raw_clicks
    else:
        try:
            total_clicks = int(raw_clicks) if raw_clicks is not None else 0
        except (TypeError, ValueError):
            total_clicks = 0

    return {
        "original_url": getattr(analytics, "original_url", ""),
        "short_code": getattr(analytics, "short_code", short_code),
        "created_at": getattr(analytics, "created_at", None),
        "expires_at": getattr(analytics, "expires_at", None),
        "total_clicks": total_clicks
    }

@router.get("/analytics/{short_code}", response_model=UrlAnalyticsResponse)
def get_analytics_alt(short_code: str, db: Session = Depends(get_db)):
    return get_url_stats(short_code=short_code, db=db)

@router.get("/urls/r/{short_code}")
@router.get("/r/{short_code}")
def redirect_url(short_code: str, db: Session = Depends(get_db)):
    result = redirect_service(db=db, short_code=short_code)
    if result is None:
        raise HTTPException(status_code=404, detail="URL not found")
    if result == "expired":
        raise HTTPException(status_code=410, detail="URL expired")
    return RedirectResponse(url=result)