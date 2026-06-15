from __future__ import annotations


def test_challenge_loading_counts(challenge_bank):
    challenges = challenge_bank.all()
    assert len(challenges) == 30

    counts = challenge_bank.counts_by_category()
    assert counts["Web"] == 6
    assert counts["Forensics"] == 5
    assert counts["Crypto Basics"] == 5
    assert counts["Linux"] == 4
    assert counts["Networking"] == 4
    assert counts["OSINT Basics"] == 3
    assert counts["Secure Coding"] == 3


def test_challenge_contract(challenge_bank):
    for challenge in challenge_bank.all():
        assert challenge.id
        assert challenge.answer
        assert challenge.acceptable_answers
        assert 2 <= len(challenge.hints) <= 3
        assert challenge.safety_note

