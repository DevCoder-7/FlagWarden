from __future__ import annotations

from app.core.quiz_engine import QuizEngine


def test_answer_checking_accepts_normalized_answer(challenge_bank):
    challenge = challenge_bank.require("crypto-002-base64")
    result = QuizEngine().check_answer(challenge, "  FLAG{BASE64_BASICS}  ")
    assert result.correct is True


def test_answer_checking_rejects_wrong_answer(challenge_bank):
    challenge = challenge_bank.require("web-002-parameterized-queries")
    result = QuizEngine().check_answer(challenge, "cross site scripting")
    assert result.correct is False

