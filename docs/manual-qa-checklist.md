# FlagWarden Manual QA Checklist

Use this checklist before recording demos or publishing screenshots.

## Telegram Functional QA

- [ ] `/start` shows FlagWarden.
- [ ] `/help` shows FlagWarden commands.
- [ ] `/daily` works.
- [ ] `/challenge` works.
- [ ] `/quiz` works.
- [ ] `/hint` works.
- [ ] `/answer flag{...}` works for the current challenge.
- [ ] Repeated solve does not double-score.
- [ ] `/score` works.
- [ ] `/profile` works.
- [ ] `/leaderboard` works.
- [ ] `/categories` works.
- [ ] `/report <feedback>` works.
- [ ] `/safety` shows legal/ethical scope.
- [ ] Unknown command suggests `/help`.
- [ ] Plain text fallback works.
- [ ] Score persists after restart through SQLite persistence.

## Branding QA

- [ ] BotFather name changed to FlagWarden.
- [ ] BotFather description uses: `Practice CTF safely. Capture flags ethically.`
- [ ] BotFather about text mentions ethical CTF cybersecurity learning.
- [ ] BotFather profile photo uploaded from `assets/logo/flagwarden-logo.png`.
- [ ] Screenshots updated with the new FlagWarden name.

## Screenshot Capture Checklist

- [ ] Capture `docs/screenshots/start.png`.
- [ ] Capture `docs/screenshots/challenge.png`.
- [ ] Capture `docs/screenshots/answer-correct.png`.
- [ ] Capture `docs/screenshots/score.png`.
- [ ] Capture `docs/screenshots/safety-policy.png`.
- [ ] Crop out usernames, private chats, phone numbers, tokens, ngrok account
      details, and admin panels.

## Safety QA

- [ ] Real-target hacking request is refused.
- [ ] Credential theft request is refused.
- [ ] Phishing request is refused.
- [ ] Malware/persistence/evasion request is refused.
- [ ] Safe conceptual CTF questions remain allowed.

