from __future__ import annotations

from datetime import date, timedelta

from app.core.scoring import ScoringService


def test_scoring_awards_less_with_hints():
    assert ScoringService.calculate_points(100, 0) == 100
    assert ScoringService.calculate_points(100, 1) == 75
    assert ScoringService.calculate_points(100, 2) == 60
    assert ScoringService.calculate_points(100, 3) == 50


def test_streak_updates():
    today = date(2026, 6, 15)
    assert ScoringService.next_streak(None, 0, today=today) == 1
    assert ScoringService.next_streak(today, 3, today=today) == 3
    assert ScoringService.next_streak(today - timedelta(days=1), 3, today=today) == 4
    assert ScoringService.next_streak(today - timedelta(days=5), 3, today=today) == 1

