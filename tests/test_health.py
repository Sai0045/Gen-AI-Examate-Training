from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_success():
    response = client.get("/health")

    assert response.status_code == 200


def test_health_endpoint_returns_expected_data():
    response = client.get("/health")
    data = response.json()

    assert data["status"] == "ok"
    assert isinstance(data["records"], int)
    assert data["records"] > 0
