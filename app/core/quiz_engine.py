from __future__ import annotations

import re
from dataclasses import dataclass

from app.core.content import Challenge


@dataclass(frozen=True)
class AnswerResult:
    correct: bool
    normalized_answer: str
    canonical_answer: str
    explanation: str


class QuizEngine:
    def check_answer(self, challenge: Challenge, submitted_answer: str) -> AnswerResult:
        normalized = normalize_answer(submitted_answer)
        accepted = {normalize_answer(challenge.answer)}
        accepted.update(normalize_answer(answer) for answer in challenge.acceptable_answers)

        return AnswerResult(
            correct=normalized in accepted,
            normalized_answer=normalized,
            canonical_answer=challenge.answer,
            explanation=challenge.explanation,
        )


def normalize_answer(value: str) -> str:
    stripped = value.strip().strip('"').strip("'").lower()
    return re.sub(r"\s+", " ", stripped)

