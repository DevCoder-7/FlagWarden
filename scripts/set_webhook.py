"""Configure Telegram webhook with the secret-token header.
Usage: python scripts/set_webhook.py https://example.com/telegram/webhook
"""

import sys

import httpx

from flagwarden.config import get_settings


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/set_webhook.py <https-webhook-url>")
    s = get_settings()
    if s.telegram_bot_token.startswith("development-"):
        raise SystemExit("Set a real TELEGRAM_BOT_TOKEN first")
    url = f"https://api.telegram.org/bot{s.telegram_bot_token}/setWebhook"
    response = httpx.post(
        url,
        json={
            "url": sys.argv[1],
            "secret_token": s.telegram_webhook_secret,
            "allowed_updates": ["message", "edited_message"],
        },
        timeout=15,
    )
    response.raise_for_status()
    print(response.json())


if __name__ == "__main__":
    main()
