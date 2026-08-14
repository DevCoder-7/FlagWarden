from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .mastery import mastery_map
from .models import ChallengeProgress, User
from .repository import all_challenges


def update_streak(user: User) -> None:
    now = datetime.now(UTC)
    if user.last_solved_at is None:
        user.streak = 1
    else:
        previous = user.last_solved_at
        if previous.tzinfo is None:
            previous = previous.replace(tzinfo=UTC)
        delta = now.date() - previous.date()
        if delta.days == 0:
            pass
        elif delta.days == 1:
            user.streak += 1
        else:
            user.streak = 1
    user.last_solved_at = now


def solved_ids(db: Session, user_id: int) -> set[str]:
    rows = db.scalars(
        select(ChallengeProgress).where(ChallengeProgress.user_id == user_id, ChallengeProgress.solved.is_(True))
    ).all()
    return {r.challenge_id for r in rows}


def recommendations(db: Session, user: User, limit: int = 3) -> list[dict]:
    challenges = all_challenges(db)
    solved = solved_ids(db, user.id)
    mastery = mastery_map(db, user.id)
    difficulty_order = {"easy": 0, "medium": 1, "hard": 2}
    candidates = []
    for challenge in challenges.values():
        if challenge.id in solved:
            continue
        avg = sum(mastery.get(s, 0.0) for s in challenge.skills) / max(1, len(challenge.skills))
        candidates.append((avg, difficulty_order[challenge.difficulty], challenge))
    candidates.sort(key=lambda x: (x[0], x[1], x[2].id))
    return [
        {
            "id": c.id,
            "title": c.title,
            "difficulty": c.difficulty,
            "skills": c.skills,
            "reason": f"Recommended to strengthen {min(c.skills, key=lambda s: mastery.get(s, 0.0))} (current mastery {min((mastery.get(s, 0.0) for s in c.skills), default=0.0):.0f}/100).",
        }
        for _, _, c in candidates[:limit]
    ]
