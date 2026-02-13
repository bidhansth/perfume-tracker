import pytest

@pytest.mark.asyncio
async def test_create_perfume(client):
    response = await client.post(
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

@pytest.mark.asyncio
async def test_list_perfumes(client):
    response = await client.get("/perfumes")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
