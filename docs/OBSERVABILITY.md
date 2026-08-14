# Observability

## Health
- `/health/live` — process is alive
- `/health/ready` — DB query succeeds

## Metrics
- `flagwarden_webhook_updates_total{result}`
- `flagwarden_challenge_solves_total{result,category}`
- `flagwarden_hint_requests_total{category}`
- `flagwarden_rate_limit_hits_total{surface}`
- `flagwarden_submission_latency_seconds`

## Logging rule
Never log raw flags, submitted answers, Telegram initData, bot token, password, or session material.

## Optional next step
OpenTelemetry can be layered on top of FastAPI for traces/log correlation once a real deployment environment exists. It is intentionally not required for the base demo.
