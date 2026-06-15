from __future__ import annotations

from pathlib import Path

import pytest

from app.config import Settings
from app.core.content import ChallengeBank
from app.db.repository import build_engine, build_session_factory, init_db


@pytest.fixture
def challenge_bank() -> ChallengeBank:
    return ChallengeBank.from_file(Path("data/challenges.json"))


@pytest.fixture
def test_settings(tmp_path: Path) -> Settings:
    return Settings(
        database_url=f"sqlite:///{tmp_path / 'test.db'}",
        challenge_data_path="data/challenges.json",
        bot_test_mode=True,
        telegram_bot_token=None,
        whatsapp_verify_token=None,
        whatsapp_access_token=None,
        whatsapp_phone_number_id=None,
        llm_provider="none",
    )


@pytest.fixture
def session_factory(test_settings: Settings):
    engine = build_engine(test_settings.database_url)
    init_db(engine)
    return build_session_factory(engine)

