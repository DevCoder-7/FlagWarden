from __future__ import annotations

import pytest

from app.bot.flow import BotResponse
from app.bot.telegram_adapter import TelegramAdapter


class FakeFlow:
    def __init__(self) -> None:
        self.calls = []

    def handle_text(self, platform, platform_user_id, text, display_name=None):
        self.calls.append((platform, platform_user_id, text, display_name))
        return BotResponse("ok")


@pytest.mark.asyncio
async def test_telegram_adapter_routes_text_to_flow():
    flow = FakeFlow()
    adapter = TelegramAdapter(flow, token=None)  # type: ignore[arg-type]

    response = await adapter.handle_text("42", "/start", "Grace")

    assert response.text == "ok"
    assert flow.calls == [("telegram", "42", "/start", "Grace")]

