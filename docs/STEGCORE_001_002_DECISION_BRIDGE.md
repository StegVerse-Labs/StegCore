# StegCore 001/002 Decision Bridge

Generated: 2026-06-17

## Assumptions

Active repo: `StegVerse-Labs/StegCore`.

The repo already has a native `DecisionResult` surface in `src/stegcore/decision.py`.

The 001/002 adapter produces a richer activation-baseline posture:

```text
allow
deny
drift
stale
refusal
override_required
```

StegCore's current native decision domain is:

```text
allow
deny
defer
```

## Done Definition

This bridge is complete when adapter results can be converted into native `DecisionResult` values without replacing `decision.py`.

## Mapping

| Adapter Status | Native Decision | Reason Code |
|---|---|---|
| allow | allow | entity_001_002.allow |
| deny | deny | entity_001_002.deny |
| drift | defer | entity_001_002.drift |
| stale | defer | entity_001_002.stale |
| refusal | defer | entity_001_002.refusal |
| override_required | defer | entity_001_002.override_required |

## Why Defer for Drift, Stale, Refusal, and Override Required

Those states are not successful permission grants.

They are also not always permanent denials.

They require additional governance work before consequence binds, so the native `DecisionResult` value is `defer` while the precise posture is preserved in `reason_code` and `reason_detail`.

## Boundary Rules Preserved

Continuity is not approval.

Execution is not admissibility.

Visibility is not governance.

Discovery is not execution authority.

Reviewer is not override authority.

A refusal must bind consequence unless explicit override authority exists.

## Validation

Run:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```
