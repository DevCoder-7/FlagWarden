from .challenges import Challenge


def score_for_solve(challenge: Challenge, hints_used: int) -> int:
    penalty = sum(h.cost for h in challenge.hints[: max(0, hints_used)])
    floor = max(1, int(challenge.points * 0.10))
    return max(floor, challenge.points - penalty)
