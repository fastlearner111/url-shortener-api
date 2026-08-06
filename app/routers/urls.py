from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import UrlCreate, UrlResponse
from app.services.shortener import create_short_url_service
from app.services.analytics import get_url_analytics
from app.services.shortener import redirect_service

router = APIRouter(prefix="/urls", tags=["URLs"])

@router.post("/shorten", response_model=UrlResponse)
def shorten(data: UrlCreate, db: Session = Depends(get_db)):
    url = create_short_url_service(db, data, owner_id=1)
    return url


@router.get("/stats/{code}")
def stats(code: str, db: Session = Depends(get_db)):
    analytics = get_url_analytics(db, code)
    if analytics is None:
        raise HTTPException(status_code=404, detail="URL not found")
    return analytics


@router.get("/r/{code}")
def redirect(code: str, db: Session = Depends(get_db)):
    result = redirect_service(db, code)

    if result is None:
        raise HTTPException(status_code=404, detail="URL not found")

    if result == "expired":
        raise HTTPException(status_code=410, detail="URL expired")

    return {"redirect_to": result}
