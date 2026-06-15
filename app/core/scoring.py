from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class ScorePreview:
    base_points: int
    hints_used: int
    points_awarded: int


class ScoringService:
    @staticmethod
    def calculate_points(base_points: int, hints_used: int) -> int:
        if hints_used <= 0:
            multiplier = 1.0
        elif hints_used == 1:
            multiplier = 0.75
        elif hints_used == 2:
            multiplier = 0.60
        else:
            multiplier = 0.50
        return max(1, round(base_points * multiplier))

    @staticmethod
    def preview(base_points: int, hints_used: int) -> ScorePreview:
        return ScorePreview(
            base_points=base_points,
            hints_used=hints_used,
            points_awarded=ScoringService.calculate_points(base_points, hints_used),
        )

    @staticmethod
    def next_streak(
        last_solved_on: date | None,
        current_streak: int,
        today: date | None = None,
    ) -> int:
        today = today or date.today()
        if last_solved_on is None:
            return 1
        if last_solved_on == today:
            return max(1, current_streak)
        if last_solved_on == today - timedelta(days=1):
            return current_streak + 1
        return 1
