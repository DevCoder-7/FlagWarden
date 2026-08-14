import json
from sqlalchemy.orm import Session
from flagwarden.audit import record_event
from flagwarden.db import get_engine


def test_audit_redacts_sensitive_values():
    with Session(get_engine()) as db:
        event = record_event(db, "test", 1, "obj", {"answer":"secret", "nested":{"token":"abc"}, "safe":"ok"})
        db.commit(); db.refresh(event)
        data = json.loads(event.details_json)
        assert data["answer"] == "[REDACTED]"
        assert data["nested"]["token"] == "[REDACTED]"
        assert data["safe"] == "ok"
