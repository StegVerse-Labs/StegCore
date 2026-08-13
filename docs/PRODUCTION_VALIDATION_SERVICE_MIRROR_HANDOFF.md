# Production Validation Service Mirror Handoff

```text
goal_id: STEGCORE-PRODUCTION-VALIDATION-SERVICE-002
repository: StegVerse-Labs/StegCore
branch: feat/manifested-validation-endpoint
parent_handoff: docs/TRANSACTION_CONTINUITY_MIRROR_HANDOFF.md
implementation_state: INSTALLED_PENDING_CI_AND_DEPLOY
release_state: NOT_RELEASED
```

## Purpose

Expose the canonical StegCore manifested transaction path at the deployed StegGate service so an upstream SDK/ingestion manifest can preserve one transaction identity while actually traversing the production StegCore service location.

```text
POST /v1/manifested-validation
```

The caller supplies the already-established `transaction_id`, canonical `AdmissibilityRequest`, input data, source/subject, and manifest metadata. The endpoint invokes `run_manifested_transaction` with that same transaction ID and therefore preserves identity through canonical StegGate evaluation and StegCore transition receipts.

## Bounded validation consequence

This endpoint is specifically for the production-routing validation lane. It refuses `external_side_effects_enabled=true` and uses a simulated consequence whose returned state explicitly records `external_side_effect=false`. It does not expose arbitrary execution authority.

## Required proof before evaluator use

```text
1. StegCore repository CI PASS.
2. Merge to main.
3. Existing Render steggate-core auto-deploy reaches merged commit.
4. Live /health exposes manifested_validation=true.
5. Live /v1/runtime-identity exposes /v1/manifested-validation.
6. SDK production validation transaction calls this deployed endpoint, not local canonical evaluation.
7. Returned transaction_id matches the upstream route manifest transaction_id.
```
