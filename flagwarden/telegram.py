from __future__ import annotations

import httpx
from sqlalchemy.orm import Session

from .bot_service import assign_challenge, next_hint, submit_answer
from .config import get_settings
from .users import get_or_create_user

HELP = """🛡️ FlagWarden commands
/start — register and see this help
/challenge — get an unsolved challenge
/daily — deterministic daily-style challenge
/random — random unsolved challenge
/hint — reveal the next progressive hint
/submit <answer> — submit the current answer
/profile — show score and streak
/app — open the learning dashboard
"""


async def send_message(chat_id: int, text: str) -> None:
    settings = get_settings()
    if settings.telegram_bot_token.startswith(
        "development-"
    ) or settings.telegram_bot_token.startswith("123456:"):
        return
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(url, json={"chat_id": chat_id, "text": text})
        response.raise_for_status()


def _extract_message(update: dict) -> tuple[int, int, str | None, str] | None:
    msg = update.get("message") or update.get("edited_message")
    if not isinstance(msg, dict):
        return None
    user = msg.get("from") or {}
    chat = msg.get("chat") or {}
    text = msg.get("text") or ""
    if not isinstance(user.get("id"), int) or not isinstance(chat.get("id"), int):
        return None
    return user["id"], chat["id"], user.get("username"), text


async def process_update(db: Session, update: dict) -> str | None:
    extracted = _extract_message(update)
    if extracted is None:
        return None
    telegram_user_id, chat_id, username, text = extracted
    user = get_or_create_user(db, telegram_user_id, username)
    command, _, arg = text.strip().partition(" ")
    command = command.lower().split("@")[0]

    if command == "/start":
        reply = HELP
    elif command in {"/challenge", "/random"}:
        reply, _ = assign_challenge(db, user, randomize=True)
    elif command == "/daily":
        reply, _ = assign_challenge(db, user, randomize=False)
    elif command == "/hint":
        reply = next_hint(db, user)
    elif command == "/submit":
        reply = submit_answer(db, user, arg) if arg else "Usage: /submit <answer>"
    elif command == "/profile":
        reply = f"🏅 Score: {user.total_score}\n🔥 Streak: {user.streak}"
    elif command == "/app":
        reply = f"Open the FlagWarden dashboard: {get_settings().miniapp_url}"
    else:
        reply = HELP

    db.commit()
    await send_message(chat_id, reply)
    return reply
