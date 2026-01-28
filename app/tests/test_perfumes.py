def test_create_perfume(client):
    response = client.post(
        "/perfumes",
        json={
            "name": "Bleu de Chanel",
            "brand": "Chanel",
            "concentration": "EDP",
            "season": "ALL",
            "available": True
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Bleu de Chanel"
    assert data["brand"] == "Chanel"

def test_list_perfumes(client):
    response = client.get("/perfumes")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
