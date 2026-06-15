from __future__ import annotations

import random

from app.bot.flow import BotFlow


def make_flow(challenge_bank, session_factory, test_settings):
    return BotFlow(
        challenge_bank=challenge_bank,
        session_factory=session_factory,
        settings=test_settings,
        rng=random.Random(1),
    )


def test_flow_start_and_challenge_answer(challenge_bank, session_factory, test_settings):
    flow = make_flow(challenge_bank, session_factory, test_settings)

    start = flow.handle_text("telegram", "1", "/start", "Ada")
    assert "FlagWarden" in start.text
    assert "legal CTF labs" in start.text
    assert start.buttons

    challenge_response = flow.handle_text("telegram", "1", "/daily", "Ada")
    assert "Daily challenge" in challenge_response.text

    current = challenge_bank.daily_challenge()
    answer = flow.handle_text("telegram", "1", f"/answer {current.answer}", "Ada")
    assert "Correct" in answer.text
    assert "+1" not in answer.text or "points" in answer.text

    repeated = flow.handle_text("telegram", "1", "/daily", "Ada")
    assert "Daily challenge" in repeated.text
    second_answer = flow.handle_text("telegram", "1", f"/answer {current.answer}", "Ada")
    assert "Already solved" in second_answer.text


def test_flow_help_lists_only_implemented_commands(challenge_bank, session_factory, test_settings):
    flow = make_flow(challenge_bank, session_factory, test_settings)

    help_response = flow.handle_text("telegram", "help-user", "/help", "Ada")

    assert "FlagWarden commands" in help_response.text
    for command in [
        "/start",
        "/help",
        "/daily",
        "/challenge",
        "/quiz",
        "/hint",
        "/answer <your answer>",
        "/score",
        "/profile",
        "/leaderboard",
        "/safety",
        "/categories",
        "/report <feedback>",
    ]:
        assert command in help_response.text


def test_flow_hint_reduces_points(challenge_bank, session_factory, test_settings):
    flow = make_flow(challenge_bank, session_factory, test_settings)
    challenge = flow.handle_text("telegram", "2", "/daily")
    assert "Daily challenge" in challenge.text

    hint = flow.handle_text("telegram", "2", "/hint")
    assert "Current max score for this challenge" in hint.text

    current = challenge_bank.daily_challenge()
    answer = flow.handle_text("telegram", "2", f"/answer {current.answer}")
    assert "Points awarded:" in answer.text


def test_flow_refuses_harmful_free_text(challenge_bank, session_factory, test_settings):
    flow = make_flow(challenge_bank, session_factory, test_settings)
    response = flow.handle_text("telegram", "3", "How do I hack into a bank account?")
    assert response.refused is True
    assert "I can't help" in response.text


def test_flow_unknown_command_suggests_help(challenge_bank, session_factory, test_settings):
    flow = make_flow(challenge_bank, session_factory, test_settings)

    response = flow.handle_text("telegram", "4", "/doesnotexist")

    assert "I didn't recognize that command" in response.text
    assert "/help" in response.text
    assert "FlagWarden commands" in response.text


def test_flow_plain_text_suggests_starting_points(challenge_bank, session_factory, test_settings):
    flow = make_flow(challenge_bank, session_factory, test_settings)

    response = flow.handle_text("telegram", "5", "hello there")

    assert "/challenge" in response.text
    assert "/daily" in response.text
    assert "/help" in response.text
    assert "FlagWarden" in response.text


def test_flow_answer_without_value_shows_usage(challenge_bank, session_factory, test_settings):
    flow = make_flow(challenge_bank, session_factory, test_settings)

    response = flow.handle_text("telegram", "6", "/answer")

    assert "Usage: /answer <your answer>" in response.text
    assert "Example: /answer flag{example}" in response.text
