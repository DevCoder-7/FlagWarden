from flagwarden.challenges import validate_pack
from flagwarden.config import get_settings
from flagwarden.verifiers import verify_submission


def test_starter_pack_validates():
    meta, challenges = validate_pack("challenge_packs/starter-pack")
    assert meta.id == "starter-pack"
    assert len(challenges) >= 2


def test_demo_hmac_challenge_answer():
    _, challenges = validate_pack("challenge_packs/starter-pack")
    challenge = next(c for c in challenges if c.id == "web-basics-001")
    assert verify_submission(challenge, "flagwarden-demo-answer", 1, get_settings().answer_pepper)
    assert not verify_submission(challenge, "wrong", 1, get_settings().answer_pepper)
