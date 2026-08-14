from .challenges import Challenge
from .security import dynamic_flag, verify_digest, normalize_answer


def verify_submission(challenge: Challenge, submitted: str, user_id: int, pepper: str) -> bool:
    cfg = challenge.verifier
    if cfg.type == "exact_hmac":
        assert cfg.digest is not None
        return verify_digest(submitted, cfg.digest, pepper)
    if cfg.type == "dynamic_hmac":
        expected = dynamic_flag(user_id, challenge.id, pepper, cfg.flag_prefix)
        return normalize_answer(submitted) == normalize_answer(expected)
    if cfg.type == "quiz_choice":
        if cfg.correct_index is None or not cfg.choices:
            return False
        expected = cfg.choices[cfg.correct_index]
        return normalize_answer(submitted) == normalize_answer(expected)
    return False
