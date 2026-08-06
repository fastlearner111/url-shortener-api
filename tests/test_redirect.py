def test_url_redirection(client):
    # 1. Create a short URL first
    create_response = client.post(
        "/urls/shorten",
        json={"original_url": "https://www.github.com"}
    )
    assert create_response.status_code == 200
    data = create_response.json()
    short_code = data["short_code"]
    
    # 2. Test the redirect route using follow_redirects=False
    response = client.get(f"/{short_code}", follow_redirects=False)
    

def test_url_not_found(client):
    # Test visiting a short code that doesn't exist
    response = client.get("/nonexistent99", follow_redirects=False)
    