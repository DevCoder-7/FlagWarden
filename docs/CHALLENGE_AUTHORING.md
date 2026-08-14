# Challenge Authoring Guide

## Lifecycle
`DRAFT -> IN_REVIEW -> APPROVED -> PUBLISHED -> DEPRECATED`

## Author checklist
- One clear learning objective.
- Explicit skills/tags.
- Difficulty justified by intended reasoning, not obscurity.
- Progressive hints with point cost.
- No plaintext secret when `exact_hmac` can be used.
- Safety scope is accurate.
- Post-solve debrief explains **why**, not just the answer.
- Remediation/defensive lesson included where applicable.
- Synthetic/authorized artifacts only.

## Verifier types
### `exact_hmac`
Use for a static answer. Generate digest with:
`flagwarden answer digest 'answer'`

### `dynamic_hmac`
The expected flag is derived from Telegram user ID + challenge ID + server secret. No per-user flag needs to be stored.

### `quiz_choice`
Use for conceptual learning checks.

## Review checklist
- Intended solve path is reproducible.
- Hints do not accidentally reveal the answer.
- Edge cases are considered.
- Answer normalization is appropriate.
- Safety scope is correct.
- Debrief is technically accurate and learner-friendly.
