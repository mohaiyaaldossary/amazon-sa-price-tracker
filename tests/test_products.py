"""Core API tests. External SerpApi calls are mocked."""

from fastapi.testclient import TestClient

from app.main import app
from app.services import amazon

client = TestClient(app)
VALID_ASIN = "B09ZFD9CBB"


def fake_product(asin: str) -> dict:
    return {
        "asin": asin.upper(),
        "product": "Sony WH-1000XM5",
        "price": 1299.0,
        "currency": "SAR",
        "source": "Amazon.sa",
        "url": f"https://www.amazon.sa/dp/{asin.upper()}",
    }


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_product_endpoint(monkeypatch):
    monkeypatch.setattr(amazon, "get_product", fake_product)
    response = client.get(f"/product/{VALID_ASIN}")
    assert response.status_code == 200
    body = response.json()
    assert body["asin"] == VALID_ASIN
    assert body["product"] == "Sony WH-1000XM5"
    assert body["price"] == 1299.0
    assert body["currency"] == "SAR"
    assert body["source"] == "Amazon.sa"
    assert isinstance(body["price"], (int, float))
