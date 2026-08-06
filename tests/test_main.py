def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "URL Shortener API is running"}

def test_shorten_url(client):
    response = client.post(
        "/urls/shorten",
        json={"original_url": "https://www.google.com"}
    )
    data = response.json()
    
    assert response.status_code == 200
    assert "short_code" in data
    assert data["original_url"] == "https://www.google.com"