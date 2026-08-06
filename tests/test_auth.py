def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "securepassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_register_duplicate_user(client):
    payload = {"email": "duplicate@example.com", "password": "password123"}
    
    # First registration should succeed
    response_1 = client.post("/auth/register", json=payload)
    assert response_1.status_code == 200
    
    # Second registration with the same email should fail (400 Bad Request)
    response_2 = client.post("/auth/register", json=payload)
    assert response_2.status_code == 400


def test_login_user(client):
    payload = {"email": "login@example.com", "password": "mypassword"}
    
    # Register the user first
    client.post("/auth/register", json=payload)

    # Attempt login with correct credentials
    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "mypassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    response = client.post(
        "/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401