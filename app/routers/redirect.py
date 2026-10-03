from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.url_service import redirect_service

router = APIRouter(tags=["Redirect"])


@router.get("/{short_code}")
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    result = redirect_service(db=db, short_code=short_code)
    if result is None:
        raise HTTPException(status_code=404, detail="URL not found")
    if result == "expired":
        raise HTTPException(status_code=410, detail="URL expired")
    return RedirectResponse(url=result, status_code=307)