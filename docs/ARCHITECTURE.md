# Architecture

## Request flow

### Telegram bot
`Telegram -> /telegram/webhook -> secret verification -> update idempotency -> bot service -> DB -> Telegram API`

### Mini App
`Telegram Mini App -> initData -> backend HMAC verification -> User/RBAC -> API -> DB`

### Challenge content
`Static Challenge Packs + Published ChallengeDraft rows -> Challenge Repository -> Learner services`

## Trust boundaries
1. Telegram infrastructure → public webhook endpoint.
2. Telegram Mini App browser → backend API.
3. Backend → PostgreSQL/SQLite.
4. Challenge authors/reviewers → published learner content.
5. Configuration/secrets → application runtime.

## Design choices
- **FastAPI** keeps HTTP boundaries explicit and testable.
- **SQLAlchemy** supports SQLite for local work and PostgreSQL for production-style deployment.
- **YAML challenge packs** make content reviewable in Git.
- **DB drafts** model editorial workflow without mutating repository files at runtime.
- **HMAC answer verification** prevents storing plaintext static answers in the challenge schema.
- **Deterministic mastery** avoids opaque AI recommendations.
