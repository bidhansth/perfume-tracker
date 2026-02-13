import pytest

@pytest.mark.asyncio
async def test_filter_perfumes_by_brand(client):
    response = await client.get("/perfumes?brand=chanel")
    assert response.status_code == 200

    data = response.json()
    assert all("Chanel" in p["brand"] for p in data["items"])
