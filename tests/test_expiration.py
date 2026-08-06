from datetime import datetime, timedelta

def test_expired_url_redirection(client):
    # 1. Create a URL that expired yesterday
    past_time = datetime.utcnow() - timedelta(days=1)
    
    create_response = client.post(
        "/urls/shorten",
        json={
            "original_url": "https://www.expired-site.com",
            "expires_at": past_time.isoformat()
        }
    )
    assert create_response.status_code == 200
    data = create_response.json()
    short_code = data["short_code"]

    # 2. Try to access the expired URL via the service redirect route (/urls/r/{code})
    response = client.get(f"/urls/r/{short_code}")
    
    # 3. Assert that it catches the expiration and returns 410 Gone
    assert response.status_code == 410
    assert response.json()["detail"] == "URL expired"