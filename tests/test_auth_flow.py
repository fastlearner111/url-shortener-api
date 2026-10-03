import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from app.core.security import create_access_token


@pytest.fixture
def real_auth_client(db_session):
    """A client that does NOT mock get_current_user, so real tokens get verified."""
    def override_get_db():
        yield db_session

    app.dependency_overrides.clear()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_login_token_works_on_protected_route(real_auth_client):
    creds = {"email": "flow@example.com", "password": "password123"}
    real_auth_client.post("/auth/register", json=creds)
    token = real_auth_client.post("/auth/login", json=creds).json()["access_token"]

    response = real_auth_client.post(
        "/urls/shorten",
        json={"original_url": "https://www.example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


def test_protected_route_rejects_missing_token(real_auth_client):
    response = real_auth_client.post(
        "/urls/shorten", json={"original_url": "https://www.example.com"}
    )
    assert response.status_code == 401


def test_token_with_wrong_claim_key_is_rejected(real_auth_client):
    # Recreates the original bug: the token carries "user_id" instead of "sub".
    bad_token = create_access_token({"user_id": "1"})
    response = real_auth_client.post(
        "/urls/shorten",
        json={"original_url": "https://www.example.com"},
        headers={"Authorization": f"Bearer {bad_token}"},
    )
    assert response.status_code == 401