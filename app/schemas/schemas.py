from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


# --- User Schemas ---
class UserCreate(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


# --- URL Schemas ---
class UrlCreate(BaseModel):
    original_url: str
    expires_at: Optional[datetime] = None 


class UrlResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    owner_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Analytics Schemas ---
class AnalyticsClickResponse(BaseModel):
    id: int
    timestamp: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    class Config:
        from_attributes = True


class UrlAnalyticsResponse(BaseModel):
    short_code: str
    total_clicks: int
    clicks: List[AnalyticsClickResponse] = []

    class Config:
        from_attributes = True


# --- Auth Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None