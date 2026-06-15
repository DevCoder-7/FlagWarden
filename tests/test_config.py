from __future__ import annotations

from app.config import Settings


def test_missing_optional_whatsapp_vars_disable_integration(tmp_path):
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'test.db'}",
        telegram_bot_token=None,
        whatsapp_verify_token=None,
        whatsapp_access_token=None,
        whatsapp_phone_number_id=None,
    )

    assert settings.whatsapp_enabled is False
    assert settings.telegram_enabled is False
    assert set(settings.missing_whatsapp_vars()) == {
        "WHATSAPP_VERIFY_TOKEN",
        "WHATSAPP_ACCESS_TOKEN",
        "WHATSAPP_PHONE_NUMBER_ID",
    }
