def test_create_purchase(client):
    # First create a perfume to reference
    perfume_response = client.post(
        "/perfumes",
        json={
            "name": "Test Perfume",
            "brand": "Test Brand",
            "concentration": "EDP",
            "season": "ALL",
            "available": True
        }
    )
    perfume_id = perfume_response.json()["id"]
    
    response = client.post(
        "/purchases",
        json={
            "perfume_id": perfume_id,
            "date": "2026-01-15",
            "price": 10000,
            "store": "Redolence",
            "ml": 100
        }
    )

    assert response.status_code == 201

def test_purchase_invalid_perfume(client):
    response = client.post(
        "/purchases",
        json={
            "perfume_id": 9999,
            "date": "2025-01-15",
            "price": 100,
            "store": "Store",
            "ml": 50
        }
    )

    assert response.status_code == 404
