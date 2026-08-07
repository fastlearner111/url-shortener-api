from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

# Define the UTC lambda helper
utc_now = lambda: datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    urls = relationship("UrlMapping", back_populates="owner")


class UrlMapping(Base):
    __tablename__ = "url_mappings"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=utc_now)
    expires_at = Column(DateTime, nullable=True)
    
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="urls")

    clicks = relationship("AnalyticsClick", back_populates="url")


class AnalyticsClick(Base):
    __tablename__ = "analytics_clicks"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utc_now)
    user_agent = Column(String)
    ip_address = Column(String)

    url_id = Column(Integer, ForeignKey("url_mappings.id"))
    url = relationship("UrlMapping", back_populates="clicks")