from collections import defaultdict, deque
from functools import lru_cache
from threading import Lock
import time

from .config import get_settings


class InMemoryRateLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            q = self._events[key]
            while q and q[0] < cutoff:
                q.popleft()
            if len(q) >= self.limit:
                return False
            q.append(now)
            return True


class RedisRateLimiter:
    """Optional distributed fixed-window limiter for multi-worker deployments."""

    def __init__(self, url: str, limit: int, window_seconds: int):
        try:
            import redis
        except ImportError as exc:
            raise RuntimeError("Install FlagWarden with the [redis] extra") from exc
        self.client = redis.Redis.from_url(url, decode_responses=True)
        self.limit = limit
        self.window_seconds = window_seconds

    def allow(self, key: str) -> bool:
        bucket = int(time.time() // self.window_seconds)
        redis_key = f"flagwarden:rl:{key}:{bucket}"
        pipe = self.client.pipeline()
        pipe.incr(redis_key)
        pipe.expire(redis_key, self.window_seconds + 2)
        count, _ = pipe.execute()
        return int(count) <= self.limit


@lru_cache
def get_rate_limiter():
    s = get_settings()
    if s.rate_limit_backend.lower() == "redis":
        return RedisRateLimiter(s.redis_url, s.rate_limit_requests, s.rate_limit_window_seconds)
    return InMemoryRateLimiter(s.rate_limit_requests, s.rate_limit_window_seconds)
