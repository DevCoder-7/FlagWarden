import secrets

from __future__ import annotations

import random
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .audit import record_event
from .config import get_settings
from .learning import solved_ids, update_streak
from .mastery import apply_solve_mastery
from .metrics import HINTS, SOLVES, SUBMISSION_LATENCY
from .models import ChallengeProgress, User
from .repository import all_challenges
from .scoring import score_for_solve
from .verifiers import verify_submission


def assign_challenge(db: Session, user: User, randomize: bool = True) -> tuple[str, str]:
    challenges = all_challenges(db)
    solved = solved_ids(db, user.id)
    available = [c for c in challenges.values() if c.id not in solved]
    if not available:
        return "🏆 You have solved every currently published challenge.", "none"
    challenge = secrets.choice(available) if randomize else sorted(available, key=lambda c: c.id)[0]
    progress = db.scalar(
        select(ChallengeProgress).where(
            ChallengeProgress.user_id == user.id,
            ChallengeProgress.challenge_id == challenge.id,
        )
    )
    if progress is None:
        progress = ChallengeProgress(user_id=user.id, challenge_id=challenge.id)
        db.add(progress)
    user.active_challenge_id = challenge.id
    record_event(db, "challenge_assigned", user.telegram_user_id, challenge.id)
    message = (
        f"🧩 {challenge.title}\n"
        f"Difficulty: {challenge.difficulty.title()} · {challenge.points} pts\n"
        f"Goal: {challenge.learning_objectives[0]}\n\n"
        "Use /hint if needed, then /submit <answer>."
    )
    return message, challenge.id


def next_hint(db: Session, user: User) -> str:
    if not user.active_challenge_id:
        return "No active challenge. Use /challenge first."
    challenges = all_challenges(db)
    challenge = challenges.get(user.active_challenge_id)
    if challenge is None:
        return "The active challenge is no longer available. Use /challenge."
    progress = db.scalar(
        select(ChallengeProgress).where(
            ChallengeProgress.user_id == user.id,
            ChallengeProgress.challenge_id == challenge.id,
        )
    )
    if progress is None:
        return "Challenge state missing. Use /challenge again."
    if progress.solved:
        return "You already solved this challenge."
    if progress.hints_used >= len(challenge.hints):
        return "No more hints are available."
    hint = challenge.hints[progress.hints_used]
    progress.hints_used += 1
    HINTS.labels(category=challenge.category).inc()
    record_event(
        db,
        "hint_requested",
        user.telegram_user_id,
        challenge.id,
        {"hint_index": progress.hints_used, "cost": hint.cost},
    )
    return f"💡 Hint {progress.hints_used}: {hint.text}\nPenalty: -{hint.cost} pts"


def submit_answer(db: Session, user: User, submitted: str) -> str:
    if not user.active_challenge_id:
        return "No active challenge. Use /challenge first."
    challenges = all_challenges(db)
    challenge = challenges.get(user.active_challenge_id)
    if challenge is None:
        return "The active challenge is unavailable."

    with SUBMISSION_LATENCY.time():
        progress = db.scalar(
            select(ChallengeProgress)
            .where(
                ChallengeProgress.user_id == user.id,
                ChallengeProgress.challenge_id == challenge.id,
            )
            .with_for_update()
        )
        if progress is None:
            return "Challenge state missing. Use /challenge again."
        if progress.solved:
            SOLVES.labels(result="duplicate", category=challenge.category).inc()
            return "✅ Already solved—no duplicate points awarded."

        settings = get_settings()
        if not verify_submission(
            challenge,
            submitted,
            user.telegram_user_id,
            settings.answer_pepper,
        ):
            SOLVES.labels(result="incorrect", category=challenge.category).inc()
            record_event(db, "submission_incorrect", user.telegram_user_id, challenge.id)
            return "❌ Not quite. Review the challenge or use /hint."

        awarded = score_for_solve(challenge, progress.hints_used)
        progress.solved = True
        progress.score_awarded = awarded
        progress.solved_at = datetime.now(UTC)
        user.total_score += awarded
        user.active_challenge_id = None
        update_streak(user)
        apply_solve_mastery(
            db,
            user.id,
            challenge.skills,
            challenge.difficulty,
            progress.hints_used,
        )
        SOLVES.labels(result="correct", category=challenge.category).inc()
        record_event(
            db,
            "challenge_solved",
            user.telegram_user_id,
            challenge.id,
            {"score_awarded": awarded, "hints_used": progress.hints_used},
        )

    d = challenge.debrief
    return (
        f"✅ Correct! +{awarded} pts\n"
        f"🔥 Streak: {user.streak}\n\n"
        f"WHY IT WORKS\n{d.why_it_works}\n\n"
        f"SECURITY CONCEPT\n{d.concept}\n\n"
        f"HOW TO REMEDIATE\n{d.remediation}"
    )
