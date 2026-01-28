def test_create_purchase(client):
    response = client.post(
        "/purchases",
        json={
            "perfume_id": 1,
            "date": "2026-01-15",
            "price": 10000,
            "store": "Redolence",
            "quantity": 100
        }
    )

    assert response.status_code == 201

def test_purchase_invalid_perfume(client):
    response = client.post(
        "/purchases",
        json={
            "perfume_id": 99,
            "date": "2025-01-15",
            "price": 100,
            "store": "Store",
            "ml": 50
        }
    )

    assert response.status_code == 404
