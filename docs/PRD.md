# Product Requirements Document — FlagWarden 2.0

## Product goal
Turn FlagWarden into a security-first CTF learning platform that demonstrates product engineering, AppSec, backend development, QA automation, challenge authoring, and DevSecOps in one coherent portfolio project.

## Primary users
1. **Learner** — solves challenges and receives progressive guidance and debriefs.
2. **Author** — creates challenge drafts.
3. **Reviewer** — validates educational quality, solve path, safety, and schema correctness.
4. **Admin** — publishes/deprecates approved challenges and manages platform policy.

## Core outcomes
- Learners see measurable progress rather than only a leaderboard.
- Challenge content is versioned and reviewable.
- Answers are not stored as plaintext by default.
- Telegram identities are authenticated server-side.
- Retry/replay behavior cannot create duplicate scoring.
- Security controls are testable and documented.

## Non-goals
- Automated exploitation of real systems.
- Real-target vulnerability scanning.
- Arbitrary command execution in challenges.
- Fully autonomous AI challenge solving.
- Kubernetes or microservice complexity without demonstrated need.

## Definition of done
- `docker compose up --build` starts the platform.
- Challenge packs validate.
- Core test suite passes.
- Mini App loads with authenticated or development-debug identity.
- Webhook rejects invalid secret and ignores duplicate update IDs.
- Secure verifier, RBAC, scoring, streak, mastery, and challenge workflow are covered by tests.
- Threat model and migration guide are present.
