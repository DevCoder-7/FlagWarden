import pytest
hypothesis = pytest.importorskip("hypothesis")
from hypothesis import given, strategies as st
from flagwarden.security import normalize_answer, dynamic_flag


@given(st.text())
def test_normalization_is_idempotent(value):
    assert normalize_answer(normalize_answer(value)) == normalize_answer(value)


@given(st.integers(min_value=1, max_value=10**9), st.text(min_size=3, max_size=30))
def test_dynamic_flag_is_deterministic(user_id, challenge_id):
    assert dynamic_flag(user_id, challenge_id, "secret") == dynamic_flag(user_id, challenge_id, "secret")
