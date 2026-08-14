import hashlib
import hmac
import json
from datetime import UTC, datetime
from urllib.parse import urlencode

import pytest

from flagwarden.security import (
    AuthenticationError,
    answer_digest,
    dynamic_flag,
    normalize_answer,
    verify_digest,
    verify_telegram_init_data,
)


def make_init_data(bot_token: str, user_id: int = 42):
    fields = {
        "auth_date": str(int(datetime.now(UTC).timestamp())),
        "query_id": "AAEAAAE",
        "user": json.dumps(
            {"id": user_id, "first_name": "Test", "username": "tester"}, separators=(",", ":")
        ),
    }
    check = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    fields["hash"] = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    return urlencode(fields)


def test_normalize_is_stable():
    assert normalize_answer("  Hello   WORLD ") == "hello world"
    assert normalize_answer(normalize_answer("  A  B ")) == "a b"


def test_hmac_answer_verification():
    digest = answer_digest("Secret Answer", "pepper")
    assert verify_digest(" secret   answer ", digest, "pepper")
    assert not verify_digest("wrong", digest, "pepper")


def test_dynamic_flags_are_user_scoped():
    a = dynamic_flag(1, "c-1", "secret")
    b = dynamic_flag(2, "c-1", "secret")
    assert a != b
    assert a == dynamic_flag(1, "c-1", "secret")


def test_valid_telegram_init_data():
    token = "123456:test-token"
    ident = verify_telegram_init_data(make_init_data(token, 77), token, 300)
    assert ident.user_id == 77
    assert ident.username == "tester"


def test_tampered_telegram_init_data_rejected():
    token = "123456:test-token"
    raw = make_init_data(token, 77).replace("%2277%22", "%2299%22")
    # Ensure any tamper is rejected. If string replacement did not hit due to encoding shape, alter query_id.
    if raw == make_init_data(token, 77):
        raw += "&extra=tamper"
    with pytest.raises(AuthenticationError):
        verify_telegram_init_data(raw, token, 300)
