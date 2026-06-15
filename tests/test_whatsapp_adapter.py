from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.bot.flow import BotResponse
from app.bot.whatsapp_adapter import WhatsAppAdapter


class FakeFlow:
    def __init__(self) -> None:
        self.calls = []

    def handle_text(self, platform, platform_user_id, text, display_name=None):
        self.calls.append((platform, platform_user_id, text, display_name))
        return BotResponse("reply")


def test_whatsapp_webhook_verification_success(test_settings):
    settings = test_settings.model_copy(update={"whatsapp_verify_token": "verify-me"})
    adapter = WhatsAppAdapter(settings, FakeFlow())  # type: ignore[arg-type]

    assert adapter.verify_webhook("subscribe", "verify-me", "12345") == "12345"


def test_whatsapp_webhook_verification_failure(test_settings):
    settings = test_settings.model_copy(update={"whatsapp_verify_token": "verify-me"})
    adapter = WhatsAppAdapter(settings, FakeFlow())  # type: ignore[arg-type]

    with pytest.raises(HTTPException) as exc:
        adapter.verify_webhook("subscribe", "wrong", "12345")
    assert exc.value.status_code == 403


def test_whatsapp_message_parsing(test_settings):
    adapter = WhatsAppAdapter(test_settings, FakeFlow())  # type: ignore[arg-type]
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "contacts": [{"wa_id": "15551234567", "profile": {"name": "Lin"}}],
                            "messages": [
                                {
                                    "from": "15551234567",
                                    "id": "wamid.1",
                                    "type": "text",
                                    "text": {"body": "/help"},
                                }
                            ],
                        }
                    }
                ]
            }
        ]
    }

    messages = adapter.parse_messages(payload)

    assert len(messages) == 1
    assert messages[0].sender_id == "15551234567"
    assert messages[0].text == "/help"
    assert messages[0].display_name == "Lin"


@pytest.mark.asyncio
async def test_whatsapp_disabled_does_not_send(test_settings):
    flow = FakeFlow()
    adapter = WhatsAppAdapter(test_settings, flow)  # type: ignore[arg-type]
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": "15551234567",
                                    "id": "wamid.1",
                                    "type": "text",
                                    "text": {"body": "/start"},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }

    result = await adapter.handle_webhook(payload)

    assert result == {"status": "disabled", "messages": 1}
    assert flow.calls == []

