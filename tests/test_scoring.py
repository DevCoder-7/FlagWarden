from flagwarden.challenges import Challenge
from flagwarden.scoring import score_for_solve


def c(points=100):
    return Challenge.model_validate(
        {
            "id": "test-001",
            "title": "Test Challenge",
            "category": "test",
            "difficulty": "easy",
            "author": "tester",
            "learning_objectives": ["learn"],
            "skills": ["test.skill"],
            "points": points,
            "hints": [{"cost": 10, "text": "h1"}, {"cost": 30, "text": "h2"}],
            "verifier": {"type": "quiz_choice", "choices": ["a", "b"], "correct_index": 0},
            "debrief": {"concept": "c", "why_it_works": "w", "remediation": "r"},
        }
    )


def test_more_hints_never_increase_score():
    ch = c()
    scores = [score_for_solve(ch, i) for i in range(4)]
    assert scores == sorted(scores, reverse=True)
    assert min(scores) > 0
