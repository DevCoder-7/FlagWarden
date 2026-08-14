# Testing Strategy

## Unit
- Answer normalization/HMAC verification
- Dynamic flag derivation
- Scoring and hint penalties
- Mastery gain
- Rate limiting
- Challenge schema validation

## Integration
- Database persistence
- Webhook secret validation
- Telegram update idempotency
- Duplicate solve prevention
- Mini App auth
- RBAC challenge workflow

## E2E target
`Telegram update -> webhook -> challenge assignment/submission -> DB -> response`

## Property-based tests
Optional Hypothesis tests cover invariants such as:
- score never becomes negative,
- more hints never increase score,
- normalization is idempotent,
- dynamic flags are deterministic per user/challenge/secret.

## Race-condition note
Production PostgreSQL uses row locking for the existing progress record during submission. Assignment creates the progress record first so the solve path has a stable row to lock.
