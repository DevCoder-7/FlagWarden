# FlagWarden Logo Assets

This folder contains logo assets for the FlagWarden Telegram bot profile and
portfolio documentation.

## Files

- `flagwarden-logo.svg` - editable vector source.
- `flagwarden-logo.png` - square PNG suitable for Telegram BotFather upload.

## Concept

- Square dark cybersecurity-themed background.
- Shield or warden-like icon.
- Small CTF flag.
- Initials `FW`.
- Designed to remain readable as a small circular Telegram avatar.
- No paid or proprietary font dependency.

## Regenerate

```bash
python scripts/generate_logo.py
```

Then upload `assets/logo/flagwarden-logo.png` in BotFather:

```text
/mybots -> select bot -> Edit Bot -> Edit Botpic
```

