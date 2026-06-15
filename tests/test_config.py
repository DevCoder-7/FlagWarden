from __future__ import annotations

from app.config import Settings


def test_missing_optional_telegram_token_disables_integration(tmp_path):
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'test.db'}",
        telegram_bot_token=None,
    )

    assert settings.telegram_enabled is False
    assert settings.llm_enabled is False
