from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import httpx
from fastapi import HTTPException

from app.bot.flow import BotFlow
from app.config import Settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IncomingWhatsAppMessage:
    sender_id: str
    text: str
    display_name: str | None = None
    message_id: str | None = None


class WhatsAppAdapter:
    def __init__(self, settings: Settings, flow: BotFlow) -> None:
        self.settings = settings
        self.flow = flow

    def verify_webhook(
        self,
        mode: str | None,
        verify_token: str | None,
        challenge: str | None,
    ) -> str:
        if not self.settings.whatsapp_verify_token:
            raise HTTPException(status_code=503, detail="WhatsApp integration is disabled")

        expected = self.settings.secret_value(self.settings.whatsapp_verify_token)
        if mode == "subscribe" and verify_token == expected and challenge is not None:
            return challenge
        raise HTTPException(status_code=403, detail="Invalid WhatsApp verification token")

    def parse_messages(self, payload: dict[str, Any]) -> list[IncomingWhatsAppMessage]:
        parsed: list[IncomingWhatsAppMessage] = []
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                contacts_by_id = {
                    contact.get("wa_id"): contact.get("profile", {}).get("name")
                    for contact in value.get("contacts", [])
                }
                for message in value.get("messages", []):
                    if message.get("type") != "text":
                        continue
                    sender = message.get("from")
                    body = message.get("text", {}).get("body")
                    if not sender or not body:
                        continue
                    parsed.append(
                        IncomingWhatsAppMessage(
                            sender_id=str(sender),
                            text=str(body),
                            display_name=contacts_by_id.get(sender),
                            message_id=message.get("id"),
                        )
                    )
        return parsed

    async def handle_webhook(self, payload: dict[str, Any]) -> dict[str, Any]:
        messages = self.parse_messages(payload)
        if not self.settings.whatsapp_enabled:
            logger.info(
                "whatsapp_webhook_received_while_disabled",
                extra={"message_count": len(messages)},
            )
            return {"status": "disabled", "messages": len(messages)}

        sent = 0
        for message in messages:
            response = self.flow.handle_text(
                "whatsapp",
                message.sender_id,
                message.text,
                message.display_name,
            )
            await self.send_text(message.sender_id, response.text)
            sent += 1

        return {"status": "ok", "messages": len(messages), "sent": sent}

    async def send_text(self, recipient: str, text: str) -> None:
        access_token = self.settings.secret_value(self.settings.whatsapp_access_token)
        phone_number_id = self.settings.whatsapp_phone_number_id
        if not access_token or not phone_number_id:
            raise RuntimeError("WhatsApp credentials are not configured")

        url = (
            f"https://graph.facebook.com/{self.settings.whatsapp_api_version}/"
            f"{phone_number_id}/messages"
        )
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
