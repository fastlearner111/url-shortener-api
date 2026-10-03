from app.main import app
from app.core.security import get_current_user
from app.models.models import User

def test_update_then_delete_url(client):
    created = client.post("/urls/shorten", json={"original_url": "https://www.example.com"})
    code = created.json()["short_code"]

    updated = client.put(f"/urls/{code}", json={"original_url": "https://www.example.org"})
    assert updated.status_code == 200

    deleted = client.delete(f"/urls/{code}")
    assert deleted.status_code == 200

    gone = client.get(f"/r/{code}")
    assert gone.status_code == 404

def test_non_owner_cannot_update_or_delete(client):
    # conftest logs every request in as user id=1, so this link belongs to user 1
    created = client.post("/urls/shorten", json={"original_url": "https://www.example.com"})
    code = created.json()["short_code"]

    # Switch the fake logged-in user to someone else, user id=2
    app.dependency_overrides[get_current_user] = lambda: User(id=2, email="other@example.com")

    update = client.put(f"/urls/{code}", json={"original_url": "https://www.evil.com"})
    assert update.status_code == 403

    delete = client.delete(f"/urls/{code}")
    assert delete.status_code == 403