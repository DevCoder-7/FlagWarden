def h(user_id): return {"X-Debug-Telegram-Id": str(user_id)}


def test_dashboard_api(client):
    r = client.get("/api/me", headers=h(10001))
    assert r.status_code == 200
    assert r.json()["role"] == "ADMIN"
    assert client.get("/api/challenges", headers=h(10001)).status_code == 200
    assert client.get("/api/recommendations", headers=h(10001)).status_code == 200


def test_user_cannot_create_challenge_draft(client):
    r = client.post("/api/admin/drafts", headers=h(20000), json={"challenge":{}})
    assert r.status_code == 403
