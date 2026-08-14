from prometheus_client import Counter, Histogram

WEBHOOK_UPDATES = Counter("flagwarden_webhook_updates_total", "Telegram webhook updates received", ["result"])
SOLVES = Counter("flagwarden_challenge_solves_total", "Challenge solve attempts", ["result", "category"])
HINTS = Counter("flagwarden_hint_requests_total", "Hints requested", ["category"])
RATE_LIMIT_HITS = Counter("flagwarden_rate_limit_hits_total", "Rate limit rejections", ["surface"])
SUBMISSION_LATENCY = Histogram("flagwarden_submission_latency_seconds", "Submission processing latency")
