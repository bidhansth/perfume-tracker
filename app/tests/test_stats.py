def test_spending_stats(client):
    response = client.get("/stats/spending")
    assert response.status_code == 200

    data = response.json()
    assert "total_spent" in data
    assert "total_purchases" in data
