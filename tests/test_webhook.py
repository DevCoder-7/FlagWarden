def update(uid=1, text="/start"):
    return {"update_id": uid, "message": {"from": {"id": 55, "username": "demo"}, "chat": {"id": 55}, "text": text}}


def test_webhook_rejects_bad_secret(client):
    r = client.post("/telegram/webhook", json=update(), headers={"X-Telegram-Bot-Api-Secret-Token":"wrong"})
    assert r.status_code == 403


def test_webhook_is_idempotent(client):
    headers={"X-Telegram-Bot-Api-Secret-Token":"test-webhook-secret"}
    first = client.post("/telegram/webhook", json=update(500), headers=headers)
    second = client.post("/telegram/webhook", json=update(500), headers=headers)
    assert first.status_code == 200
    assert first.json()["duplicate"] is False
    assert second.status_code == 200
    assert second.json()["duplicate"] is True
