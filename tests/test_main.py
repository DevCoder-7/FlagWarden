from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint(test_settings):
    app = create_app(test_settings)
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["challenge_count"] == 30
    assert payload["whatsapp_enabled"] is False

