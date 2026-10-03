def test_update_then_delete_url(client):
    created = client.post("/urls/shorten", json={"original_url": "https://www.example.com"})
    code = created.json()["short_code"]

    updated = client.put(f"/urls/{code}", json={"original_url": "https://www.example.org"})
    assert updated.status_code == 200

    deleted = client.delete(f"/urls/{code}")
    assert deleted.status_code == 200

    gone = client.get(f"/r/{code}")
    assert gone.status_code == 404