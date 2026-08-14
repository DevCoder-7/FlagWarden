from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import SkillMastery

DIFFICULTY_WEIGHT = {"easy": 1.0, "medium": 1.5, "hard": 2.0}


def mastery_gain(difficulty: str, hints_used: int) -> float:
    base = 10.0 * DIFFICULTY_WEIGHT.get(difficulty, 1.0)
    return max(2.0, base - 2.0 * max(0, hints_used))


def apply_solve_mastery(db: Session, user_id: int, skills: list[str], difficulty: str, hints_used: int) -> None:
    gain = mastery_gain(difficulty, hints_used)
    for skill in skills:
        row = db.scalar(select(SkillMastery).where(SkillMastery.user_id == user_id, SkillMastery.skill == skill))
        if row is None:
            row = SkillMastery(user_id=user_id, skill=skill, score=0.0)
            db.add(row)
            db.flush()
        row.score = min(100.0, round(row.score + gain, 2))


def mastery_map(db: Session, user_id: int) -> dict[str, float]:
    rows = db.scalars(select(SkillMastery).where(SkillMastery.user_id == user_id)).all()
    return {r.skill: r.score for r in rows}
