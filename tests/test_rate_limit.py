from flagwarden.rate_limit import InMemoryRateLimiter


def test_memory_rate_limiter_blocks_after_limit():
    limiter = InMemoryRateLimiter(limit=2, window_seconds=60)
    assert limiter.allow("u")
    assert limiter.allow("u")
    assert not limiter.allow("u")
