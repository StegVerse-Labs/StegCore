# Deployment Runbook (v1.0)
**Status:** Planned
**Generated:** 2026-01-10

## Minimal bring-up order
1. Create `StegCore` repo and add this bundle.
2. Create Issue #1 (Init StegCore baseline).
3. Wire StegTV tiers + wallets (Issue #2).
4. Create StegVA + StegSocial-Bridge repos (Issues #3 and #5).
5. Turn on Healer drift checks (Issue #6).

## Smoke test
Run `python tools/EntitySupervisor.py` and confirm `out/entity_plan.json` exists.
