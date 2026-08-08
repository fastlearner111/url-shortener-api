from app.models.url import Url
from datetime import datetime

def test_url_model_fields():
    url = Url(
        id=1,
        original_url="https://example.com",
        short_code="abc123",
        created_at=datetime.utcnow(),
        clicks=0,
        is_active=True
    )

    assert url.id == 1
    assert url.original_url == "https://example.com"
    assert url.short_code == "abc123"
    assert isinstance(url.created_at, datetime)
    assert url.clicks == 0
    assert url.is_active is True


def test_url_model_click_increment():
    url = Url(
        id=1,
        original_url="https://example.com",
        short_code="abc123",
        created_at=datetime.utcnow(),
        clicks=0,
        is_active=True
    )

    url.clicks += 1
    assert url.clicks == 1


def test_url_model_deactivation():
    url = Url(
        id=1,
        original_url="https://example.com",
        short_code="abc123",
        created_at=datetime.utcnow(),
        clicks=0,
        is_active=True
    )

    url.is_active = False
    assert url.is_active is False
