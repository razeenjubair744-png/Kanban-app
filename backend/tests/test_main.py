from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "Kanban Studio" in response.text
