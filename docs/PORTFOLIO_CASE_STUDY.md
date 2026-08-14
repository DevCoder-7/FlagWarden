# Portfolio Case Study Outline

## One-line pitch
FlagWarden is a security-first CTF learning and challenge-management platform for Telegram, built with FastAPI, secure Telegram integrations, challenge-pack validation, adaptive skill tracking, RBAC authoring, automated testing, and DevSecOps controls.

## Problem
CTF learners often practice through disconnected challenge lists. FlagWarden creates a structured learning loop with progress, hints, debriefs, skill mastery, and recommendations while treating platform security as a first-class engineering requirement.

## Engineering decisions to discuss in interviews
- Why idempotency matters for webhook retries.
- Why challenge answers are HMAC-verified instead of stored plaintext.
- Why Mini App `initDataUnsafe` is not trusted.
- Why challenge publication has separate author/reviewer/admin roles.
- Why deterministic recommendations are easier to explain and test than an LLM.
- Why SQLite remains useful locally while PostgreSQL is available for production-style deployment.

## Suggested screenshots
1. Mini App dashboard.
2. Challenge Pack validator CLI.
3. Swagger API docs.
4. Challenge Studio draft list.
5. CI passing.
6. Threat model / architecture diagram.

## CV bullet candidates
- Built FlagWarden, a security-first Telegram CTF learning and challenge-management platform using FastAPI, SQLAlchemy/PostgreSQL, a Telegram Mini App, adaptive skill tracking, and versioned challenge packs.
- Implemented webhook authentication, update idempotency, HMAC/dynamic answer verification, RBAC challenge publishing, rate limiting, audit logging, and backend validation of Telegram Mini App identity.
- Added automated unit/integration/security regression tests and a DevSecOps pipeline with CodeQL, Bandit, dependency auditing, Dependabot, and Dockerized deployment.
