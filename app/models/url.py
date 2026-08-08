from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from app.core.database import Base

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    last_accessed_at = Column(DateTime, nullable=True)
    clicks = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

# Alias to satisfy test suite looking for 'Url'
Url = URL