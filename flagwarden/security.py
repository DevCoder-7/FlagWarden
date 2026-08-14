from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from urllib.parse import parse_qsl


class AuthenticationError(ValueError):
    pass


def normalize_answer(value: str) -> str:
    return " ".join(value.strip().lower().split())


def answer_digest(answer: str, pepper: str) -> str:
    normalized = normalize_answer(answer).encode()
    return hmac.new(pepper.encode(), normalized, hashlib.sha256).hexdigest()


def verify_digest(answer: str, stored_digest: str, pepper: str) -> bool:
    actual = answer_digest(answer, pepper)
    return hmac.compare_digest(actual, stored_digest.lower())


def dynamic_flag(user_id: int, challenge_id: str, secret: str, prefix: str = "FLAGWARDEN") -> str:
    msg = f"{user_id}:{challenge_id}".encode()
    token = hmac.new(secret.encode(), msg, hashlib.sha256).hexdigest()[:24]
    return f"{prefix}{{{token}}}"


def verify_webhook_secret(received: str | None, expected: str) -> bool:
    if not received:
        return False
    return hmac.compare_digest(received, expected)


@dataclass(frozen=True)
class TelegramIdentity:
    user_id: int
    username: str | None
    first_name: str | None
    auth_date: int


def verify_telegram_init_data(
    raw_init_data: str, bot_token: str, max_age_seconds: int = 300
) -> TelegramIdentity:
    if not raw_init_data:
        raise AuthenticationError("Missing Telegram initData")

    pairs = dict(parse_qsl(raw_init_data, keep_blank_values=True))
    received_hash = pairs.pop("hash", None)
    if not received_hash:
        raise AuthenticationError("Missing initData hash")

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
    # Telegram Mini Apps docs: HMAC-SHA256(bot_token) using constant 'WebAppData' as the key.
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(computed_hash, received_hash):
        raise AuthenticationError("Invalid Telegram initData signature")

    try:
        auth_date = int(pairs["auth_date"])
    except (KeyError, ValueError) as exc:
        raise AuthenticationError("Invalid auth_date") from exc

    now = int(datetime.now(UTC).timestamp())
    age = now - auth_date
    if age < -30 or age > max_age_seconds:
        raise AuthenticationError("Expired or future Telegram initData")

    try:
        user = json.loads(pairs["user"])
        user_id = int(user["id"])
    except (KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
        raise AuthenticationError("Invalid Telegram user payload") from exc

    return TelegramIdentity(
        user_id=user_id,
        username=user.get("username"),
        first_name=user.get("first_name"),
        auth_date=auth_date,
    )
