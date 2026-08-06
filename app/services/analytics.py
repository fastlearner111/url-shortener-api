from sqlalchemy.orm import Session
from app.repositories.crud import record_click, get_clicks_for_url, get_url_by_code
from app.schemas.schemas import UrlAnalyticsResponse, AnalyticsClickResponse

def process_click(db: Session, url_id: int, user_agent: str, ip_address: str):
    return record_click(db, url_id, user_agent, ip_address)


def get_url_analytics(db: Session, code: str):
    # 1. Look up the URL in the database using the short code string
    db_url = get_url_by_code(db, code)
    if not db_url:
        return None
        
    # 2. Get clicks using the database record's integer ID
    clicks = get_clicks_for_url(db, db_url.id)
    
    # 3. Return response with all required fields (url_id, short_code, total_clicks, clicks)
    return UrlAnalyticsResponse(
        url_id=db_url.id,
        short_code=db_url.short_code,
        total_clicks=len(clicks),
        clicks=[
            AnalyticsClickResponse(
                timestamp=c.timestamp,
                user_agent=c.user_agent,
                ip_address=c.ip_address
            )
            for c in clicks
        ]
    )