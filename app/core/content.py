from __future__ import annotations

import json
import random
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator

Difficulty = Literal["beginner", "intermediate"]


class Challenge(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    category: str = Field(min_length=1)
    difficulty: Difficulty
    prompt: str = Field(min_length=1)
    answer: str = Field(min_length=1)
    acceptable_answers: list[str] = Field(min_length=1)
    hints: list[str] = Field(min_length=2, max_length=3)
    explanation: str = Field(min_length=1)
    points: int = Field(gt=0)
    safety_note: str = Field(min_length=1)

    @field_validator("category", "title", "answer")
    @classmethod
    def strip_required_strings(cls, value: str) -> str:
        return value.strip()


class ChallengeBank:
    def __init__(self, challenges: list[Challenge]):
        if not challenges:
            raise ValueError("At least one challenge is required")

        duplicate_ids = [
            challenge_id
            for challenge_id, count in Counter(challenge.id for challenge in challenges).items()
            if count > 1
        ]
        if duplicate_ids:
            raise ValueError(f"Duplicate challenge IDs: {', '.join(sorted(duplicate_ids))}")

        self._challenges = challenges
        self._by_id = {challenge.id: challenge for challenge in challenges}

    @classmethod
    def from_file(cls, path: str | Path) -> ChallengeBank:
        content_path = Path(path)
        with content_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        if not isinstance(payload, list):
            raise ValueError("Challenge file must contain a JSON array")

        return cls([Challenge.model_validate(item) for item in payload])

    def all(self) -> list[Challenge]:
        return list(self._challenges)

    def get(self, challenge_id: str) -> Challenge | None:
        return self._by_id.get(challenge_id)

    def require(self, challenge_id: str) -> Challenge:
        challenge = self.get(challenge_id)
        if not challenge:
            raise KeyError(f"Unknown challenge ID: {challenge_id}")
        return challenge

    def categories(self) -> list[str]:
        return sorted({challenge.category for challenge in self._challenges})

    def counts_by_category(self) -> dict[str, int]:
        return dict(Counter(challenge.category for challenge in self._challenges))

    def random_challenge(
        self,
        category: str | None = None,
        exclude_ids: set[str] | None = None,
        rng: random.Random | None = None,
    ) -> Challenge:
        exclude_ids = exclude_ids or set()
        candidates = [
            challenge
            for challenge in self._challenges
            if challenge.id not in exclude_ids
            and (category is None or challenge.category == category)
        ]
        if not candidates:
            candidates = [
                challenge
                for challenge in self._challenges
                if category is None or challenge.category == category
            ]
        if not candidates:
            raise ValueError(f"No challenges available for category: {category}")
        picker = rng or random
        return picker.choice(candidates)

    def daily_challenge(self, day: date | None = None) -> Challenge:
        selected_day = day or date.today()
        index = selected_day.toordinal() % len(self._challenges)
        return self._challenges[index]
