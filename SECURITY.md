# Security Policy

## Scope
FlagWarden is a legal CTF/lab learning platform. Security issues in the application itself are welcome as responsible reports.

## Do not
- Test third-party systems using this project without explicit authorization.
- Commit real Telegram bot tokens, webhook secrets, answer peppers, private keys, or credentials.
- Add destructive payloads, persistence, stealth/evasion, or autonomous exploitation features.

## Secret handling
Use environment variables locally and a managed secret store in production. `.env` is gitignored.

## Evidence handling
If screenshots/logs are used in a portfolio, redact tokens, user identifiers that are not needed, and all answer/flag material.
