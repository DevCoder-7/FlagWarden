# FlagWarden 1.x -> 2.0 Migration Guide

This v2 package is an enhanced rebuild based on the publicly described FlagWarden feature set. It is structured so existing content can be migrated cleanly instead of copying older coupling/technical debt.

## Feature mapping

| 1.x capability | 2.0 destination |
|---|---|
| Telegram commands | `flagwarden/telegram.py` + `bot_service.py` |
| SQLite progress | SQLAlchemy models; SQLite or PostgreSQL |
| Daily/random challenge | `assign_challenge()` |
| Progressive hints | `next_hint()` + challenge YAML `hints` |
| Answer validation | `verifiers.py` + HMAC/dynamic verifier |
| Scoring | `scoring.py` |
| Streak tracking | `learning.py` |
| Rate limiting | `rate_limit.py` adapter |
| FastAPI webhook | `/telegram/webhook` |
| `/health` | `/health/live` + `/health/ready` |
| `/metrics` | Prometheus metrics |
| Automated tests | expanded `tests/` suite |
| Manual QA checklist | `docs/TESTING.md` + CI |

## Migrate challenge content
1. Create a pack directory under `challenge_packs/`.
2. Convert each challenge to the v2 YAML schema.
3. Generate HMAC digests instead of storing static answers.
4. Add `learning_objectives`, `skills`, `safety`, and `debrief`.
5. Run `flagwarden pack validate <pack-dir>`.

## Migrate users/progress
If 1.x already has SQLite tables, write a one-off importer that reads old rows and writes `User` / `ChallengeProgress` rows. Do not modify old DB files in place. Validate counts and score totals before switching.

## Cutover
1. Freeze content changes in 1.x.
2. Back up the old database.
3. Import data into a fresh v2 database.
4. Validate challenge IDs and progress mapping.
5. Configure Telegram bot/webhook secrets.
6. Run smoke tests.
7. Switch webhook URL.
8. Keep 1.x backup for rollback.
