from __future__ import annotations

import json
from sqlalchemy import select
from sqlalchemy.orm import Session

from .challenges import Challenge, load_all_packs
from .config import get_settings
from .models import ChallengeDraft, DraftStatus


def static_challenges() -> dict[str, Challenge]:
    return load_all_packs(get_settings().challenge_pack_root)


def published_draft_challenges(db: Session) -> dict[str, Challenge]:
    rows = db.scalars(select(ChallengeDraft).where(ChallengeDraft.status == DraftStatus.PUBLISHED.value)).all()
    out = {}
    for row in rows:
        challenge = Challenge.model_validate(json.loads(row.content_json))
        out[challenge.id] = challenge
    return out


def all_challenges(db: Session) -> dict[str, Challenge]:
    result = static_challenges()
    result.update(published_draft_challenges(db))
    return result
