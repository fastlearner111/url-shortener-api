def test_url_analytics_tracking(client):
    # 1. Shorten a URL
    create_response = client.post(
        "/urls/shorten",
        json={"original_url": "https://www.analytics-test.com"}
    )
    data = create_response.json()
    short_code = data["short_code"]

    # 2. Hit the analytics stats endpoint
    stats_response = client.get(f"/urls/stats/{short_code}")
    
    assert stats_response.status_code == 200
    stats_data = stats_response.json()
    assert stats_data["short_code"] == short_code
    assert "total_clicks" in stats_data
    assert isinstance(stats_data["clicks"], list)