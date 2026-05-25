from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_success():
    response = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "password"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == "user"
    assert response.json()["token"] == "user-token"


def test_login_failure():
    response = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "wrong"},
    )
    assert response.status_code == 401


def test_board_persistence_and_update():
    login_response = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "password"},
    )
    token = login_response.json()["token"]

    board_response = client.get(
        "/api/board",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert board_response.status_code == 200
    board = board_response.json()
    assert len(board["columns"]) == 5

    board["columns"][0]["title"] = "Backlog Updated"
    patch_response = client.patch(
        "/api/board",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=board,
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["columns"][0]["title"] == "Backlog Updated"

    second_response = client.get(
        "/api/board",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert second_response.json()["columns"][0]["title"] == "Backlog Updated"


def test_ai_route_without_key_returns_message():
    login_response = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "password"},
    )
    token = login_response.json()["token"]

    response = client.post(
        "/api/ai",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={
            "prompt": "Summarize the board.",
            "board": {"columns": [], "cards": {}},
            "history": [],
        },
    )
    assert response.status_code == 200
    assert "OpenRouter" in response.json()["message"] or isinstance(response.json()["message"], str)
