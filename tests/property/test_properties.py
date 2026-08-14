import pytest

hypothesis = pytest.importorskip("hypothesis")

from hypothesis import given
from hypothesis import strategies as st

from flagwarden.security import dynamic_flag, normalize_answer


@given(st.text())
def test_normalization_is_idempotent(value):
    assert normalize_answer(normalize_answer(value)) == normalize_answer(value)


@given(st.integers(min_value=1, max_value=10**9), st.text(min_size=3, max_size=30))
def test_dynamic_flag_is_deterministic(user_id, challenge_id):
    assert dynamic_flag(user_id, challenge_id, "secret") == dynamic_flag(user_id, challenge_id, "secret")
