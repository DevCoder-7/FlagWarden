from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint(test_settings):
    app = create_app(test_settings)
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload == {
        "status": "ok",
        "app": "FlagWarden",
        "environment": "local",
        "telegram_enabled": False,
        "llm_enabled": False,
        "challenge_count": 30,
    }
