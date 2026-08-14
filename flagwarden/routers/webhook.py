from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..metrics import RATE_LIMIT_HITS, WEBHOOK_UPDATES
from ..models import ProcessedUpdate
from ..rate_limit import get_rate_limiter
from ..security import verify_webhook_secret
from ..telegram import process_update

router = APIRouter(prefix="/telegram", tags=["telegram"])


def _telegram_actor_id(update: dict) -> int | None:
    message = update.get("message") or update.get("edited_message") or {}
    actor = message.get("from") or {}
    value = actor.get("id")
    return value if isinstance(value, int) else None


@router.post("/webhook")
async def telegram_webhook(
    update: dict,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    settings = get_settings()
    if not verify_webhook_secret(
        x_telegram_bot_api_secret_token,
        settings.telegram_webhook_secret,
    ):
        WEBHOOK_UPDATES.labels(result="unauthorized").inc()
        raise HTTPException(status_code=403, detail="invalid webhook secret")

    update_id = update.get("update_id")
    if not isinstance(update_id, int):
        WEBHOOK_UPDATES.labels(result="invalid").inc()
        raise HTTPException(status_code=400, detail="missing integer update_id")

    # Insert the idempotency record before business logic. Telegram retries a failed
    # webhook delivery, so a unique update_id prevents duplicate score mutations.
    db.add(ProcessedUpdate(update_id=update_id))
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        WEBHOOK_UPDATES.labels(result="duplicate").inc()
        return {"ok": True, "duplicate": True}

    actor_id = _telegram_actor_id(update)
    if actor_id is not None and not get_rate_limiter().allow(f"telegram:{actor_id}"):
        # Return 2xx so Telegram does not retry a deliberately rate-limited update.
        db.commit()
        RATE_LIMIT_HITS.labels(surface="telegram").inc()
        WEBHOOK_UPDATES.labels(result="rate_limited").inc()
        return {"ok": True, "duplicate": False, "rate_limited": True}

    reply = await process_update(db, update)
    db.commit()
    WEBHOOK_UPDATES.labels(result="processed").inc()
    return {"ok": True, "duplicate": False, "rate_limited": False, "reply_preview": reply}
