import json

from sqlalchemy.orm import Session

from .models import AuditEvent

SENSITIVE_KEYS = {"answer", "flag", "token", "password", "session", "init_data", "bot_token"}


def _sanitize(value):
    if isinstance(value, dict):
        return {
            k: ("[REDACTED]" if k.lower() in SENSITIVE_KEYS else _sanitize(v))
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [_sanitize(v) for v in value]
    return value


def record_event(
    db: Session,
    event_type: str,
    actor_telegram_id: int | None = None,
    object_id: str | None = None,
    details: dict | None = None,
):
    event = AuditEvent(
        event_type=event_type,
        actor_telegram_id=actor_telegram_id,
        object_id=object_id,
        details_json=json.dumps(_sanitize(details or {}), separators=(",", ":"), sort_keys=True),
    )
    db.add(event)
    return event
