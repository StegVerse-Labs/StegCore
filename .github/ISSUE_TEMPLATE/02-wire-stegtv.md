---
name: "Feat: StegTV Vault tiers + entity wallet registry"
about: "StegVerse build step (v1.2)"
---

## Goal
Wire StegTV to reflect `policies/vault_tiers.yml` and `finance/FinLedger_init.yml` from StegCore.

## Tasks
- Mirror vault tiers in StegTV config
- Add entity wallet registry
- Add internal read-only endpoints for tiers and wallets
- No secrets committed

## Acceptance criteria
- Tiers and wallets are queryable internally

