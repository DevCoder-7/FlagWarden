from __future__ import annotations

import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..audit import record_event
from ..auth import current_user, require_role
from ..challenges import Challenge
from ..db import get_db
from ..learning import recommendations, solved_ids
from ..mastery import mastery_map
from ..models import ChallengeDraft, DraftStatus, Role, User
from ..repository import all_challenges

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/me")
def me(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return {
        "telegram_user_id": user.telegram_user_id,
        "username": user.username,
        "role": user.role,
        "total_score": user.total_score,
        "streak": user.streak,
        "active_challenge_id": user.active_challenge_id,
        "skills": mastery_map(db, user.id),
        "solved": sorted(solved_ids(db, user.id)),
    }


@router.get("/challenges")
def list_challenges(user: User = Depends(current_user), db: Session = Depends(get_db)):
    solved = solved_ids(db, user.id)
    out = []
    for c in all_challenges(db).values():
        out.append({
            "id": c.id,
            "title": c.title,
            "category": c.category,
            "difficulty": c.difficulty,
            "points": c.points,
            "skills": c.skills,
            "solved": c.id in solved,
            "learning_objectives": c.learning_objectives,
        })
    return sorted(out, key=lambda x: x["id"])


@router.get("/recommendations")
def recommend(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return recommendations(db, user)


class DraftPayload(BaseModel):
    challenge: dict


@router.post("/admin/drafts")
def create_draft(
    payload: DraftPayload,
    user: User = Depends(require_role(Role.AUTHOR)),
    db: Session = Depends(get_db),
):
    challenge = Challenge.model_validate(payload.challenge)
    row = ChallengeDraft(
        challenge_id=challenge.id,
        version=challenge.version,
        status=DraftStatus.DRAFT.value,
        author_telegram_id=user.telegram_user_id,
        content_json=challenge.model_dump_json(),
    )
    db.add(row)
    record_event(db, "challenge_draft_created", user.telegram_user_id, challenge.id)
    db.commit()
    db.refresh(row)
    return {"id": row.id, "challenge_id": row.challenge_id, "status": row.status}


@router.get("/admin/drafts")
def list_drafts(
    user: User = Depends(require_role(Role.AUTHOR)),
    db: Session = Depends(get_db),
):
    rows = db.scalars(select(ChallengeDraft).order_by(ChallengeDraft.id.desc())).all()
    return [
        {
            "id": r.id,
            "challenge_id": r.challenge_id,
            "version": r.version,
            "status": r.status,
            "author_telegram_id": r.author_telegram_id,
            "reviewer_telegram_id": r.reviewer_telegram_id,
        }
        for r in rows
    ]


def _draft_or_404(db: Session, draft_id: int) -> ChallengeDraft:
    row = db.get(ChallengeDraft, draft_id)
    if row is None:
        raise HTTPException(status_code=404, detail="draft not found")
    return row


@router.post("/admin/drafts/{draft_id}/submit")
def submit_draft(
    draft_id: int,
    user: User = Depends(require_role(Role.AUTHOR)),
    db: Session = Depends(get_db),
):
    row = _draft_or_404(db, draft_id)
    if row.author_telegram_id != user.telegram_user_id and user.role != Role.ADMIN.value:
        raise HTTPException(status_code=403, detail="only the author or admin can submit this draft")
    if row.status != DraftStatus.DRAFT.value:
        raise HTTPException(status_code=409, detail="draft is not in DRAFT state")
    Challenge.model_validate(json.loads(row.content_json))
    row.status = DraftStatus.IN_REVIEW.value
    record_event(db, "challenge_submitted_for_review", user.telegram_user_id, row.challenge_id)
    db.commit()
    return {"id": row.id, "status": row.status}


@router.post("/admin/drafts/{draft_id}/approve")
def approve_draft(
    draft_id: int,
    user: User = Depends(require_role(Role.REVIEWER)),
    db: Session = Depends(get_db),
):
    row = _draft_or_404(db, draft_id)
    if row.status != DraftStatus.IN_REVIEW.value:
        raise HTTPException(status_code=409, detail="draft is not in review")
    row.status = DraftStatus.APPROVED.value
    row.reviewer_telegram_id = user.telegram_user_id
    record_event(db, "challenge_approved", user.telegram_user_id, row.challenge_id)
    db.commit()
    return {"id": row.id, "status": row.status}


@router.post("/admin/drafts/{draft_id}/publish")
def publish_draft(
    draft_id: int,
    user: User = Depends(require_role(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    row = _draft_or_404(db, draft_id)
    if row.status != DraftStatus.APPROVED.value:
        raise HTTPException(status_code=409, detail="draft must be approved before publishing")
    challenge = Challenge.model_validate(json.loads(row.content_json))
    content = challenge.model_copy(update={"status": "published"})
    row.content_json = content.model_dump_json()
    row.status = DraftStatus.PUBLISHED.value
    record_event(db, "challenge_published", user.telegram_user_id, row.challenge_id)
    db.commit()
    return {"id": row.id, "status": row.status}
