import os
import redis
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter(tags=["Monitoring"])

@router.get("/health", status_code=status.HTTP_200_OK)
def health_check(db: Session = Depends(get_db)):
    health_status = {
        "status": "healthy",
        "database": "connected",
        "redis": "connected"
    }
    
    # 1. Test PostgreSQL Connection
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        health_status["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # 2. Test Redis Connection
    try:
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        r = redis.from_url(redis_url)
        r.ping()
    except Exception as e:
        health_status["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    return health_status