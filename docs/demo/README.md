# FlagWarden Demo Guide

This folder contains materials for preparing a short GitHub or LinkedIn demo of
FlagWarden.

## Files

| Asset | Path | Notes |
|---|---|---|
| Demo GIF | `docs/demo/flagwarden-demo.gif` | Optional generated output from real screenshots. |
| Demo script | `docs/demo/demo-script.md` | 30-60 second recording plan, captions, and privacy checks. |
| LinkedIn draft | `docs/demo/linkedin-post-draft.md` | Ready-to-edit LinkedIn project announcement. |

## Workflow

1. Run FlagWarden locally and connect Telegram through a temporary webhook.
2. Capture real screenshots listed in `docs/screenshots/README.md`.
3. Record a 30-60 second video using `demo-script.md`.
4. Optionally generate a GIF:

   ```bash
   python -m pip install pillow
   python scripts/make_demo_gif.py
   ```

5. Review the output for privacy before publishing.
