# Implementation / Migration Roadmap

## Phase 1 — Local hardening (1–2 days)
- Configure real local secrets.
- Run SQLite version.
- Validate webhook tests.
- Review challenge schema and safety rules.

## Phase 2 — Migrate original FlagWarden content (1–3 days)
- Convert existing challenges to Challenge Packs.
- Replace plaintext answers with HMAC digests where applicable.
- Add learning objectives, skill tags, safety scope, and debriefs.
- Preserve challenge IDs where user progress depends on them.

## Phase 3 — Data migration (0.5–1 day)
- Export old SQLite rows.
- Import users/progress into fresh v2 DB.
- Compare row counts, score totals, and solved challenge IDs.

## Phase 4 — Product UX (1–2 days)
- Brand Mini App with final screenshots/colors.
- Register Mini App in BotFather.
- Add final challenge artwork/metadata.
- Test USER/AUTHOR/REVIEWER/ADMIN journeys.

## Phase 5 — Production-style deployment (1–2 days)
- Start PostgreSQL stack.
- Run Alembic migration.
- Configure HTTPS webhook.
- Enable real secret token.
- Optionally enable Redis and OpenTelemetry.

## Phase 6 — Portfolio packaging (0.5–1 day)
- Record a 60–90 second demo.
- Add architecture screenshot.
- Add CI passing screenshot.
- Add one security-control case study: webhook replay or answer-protection design.
- Update CV with only claims you personally validated.
