---
name: "Init: StegVA-Liaison SISP service"
about: "StegVerse build step (v1.2)"
---

## Goal
Create StegVA repo and scaffold SISP service skeleton.

## Tasks
- Create repo `StegVA` (via SCW or manual)
- Scaffold FastAPI app with placeholder routes:
  - POST /v1/intake/claim
  - POST /v1/submit/va
- Consent ledger checks required
- Tag persisted records `risk_tag: high`

## Acceptance criteria
- Service runs locally
- No plaintext PII persisted

