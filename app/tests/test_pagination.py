def test_pagination_limit(client):
    response = client.get("/perfumes?limit=1")
    assert response.status_code == 200

    data = response.json()
    assert len(data["items"]) <= 1
