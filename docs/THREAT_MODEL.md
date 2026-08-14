# Threat Model

## Assets
- Telegram bot token
- Webhook secret
- Answer pepper / dynamic-flag secret
- Learner identity and progress
- Score integrity
- Challenge answer/verifier material
- Author/reviewer/admin privileges
- Published challenge integrity
- Audit records

## Threats and controls

| Threat | Primary control | Verification |
|---|---|---|
| Forged Telegram webhook | Secret-token header + constant-time compare | Webhook security test |
| Telegram retry duplicates scoring | Unique `update_id` idempotency record | Duplicate webhook test |
| Duplicate solve / race | Persistent progress row + row lock + solved guard | Scoring/duplicate tests |
| Plaintext answer leakage | HMAC verifier / dynamic verifier | Verifier tests + repository review |
| Mini App identity spoofing | Backend validation of raw `initData` + `auth_date` | Auth unit tests |
| Privilege escalation | RBAC dependency + configured role mapping | API role tests |
| Malicious challenge publication | Pydantic schema + review/approve/publish states | Workflow tests |
| Sensitive logging | Sanitized structured audit helper | Audit test |
| Dependency vulnerabilities | Dependabot + pip-audit + CodeQL/Bandit | CI |
| Excessive requests | Rate limiter boundary; Redis adapter optional | Rate-limit tests |

## Safety boundary
FlagWarden content must be `concept_only`, `ctf_only`, or `lab_only`. Challenge authors must not publish real third-party credentials, targets, exploit infrastructure, or destructive instructions.

## Residual risks / future work
- Distributed rate limiting requires Redis when multiple workers are used.
- A true production deployment should use managed secret storage.
- Published DB challenges should have signed/exported content bundles for stronger supply-chain integrity.
