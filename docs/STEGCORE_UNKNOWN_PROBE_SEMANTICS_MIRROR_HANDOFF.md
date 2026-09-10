# StegCore Unknown Probe Semantics Mirror Handoff

Goal Task ID: `STEGCORE-UNKNOWN-PROBE-SEMANTICS-001`
Parent Goal Task ID: `SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001`
Repository: `StegVerse-Labs/StegCore`
Status: `COMPLETE_VALIDATED`

## Objective

Preserve unestablished governance predicates as explicit UNKNOWN state through the StegGate -> three-layer boundary. Unknown must not be coerced to false/stale. Ambiguity affecting admissibility must fail closed as probe-required evidence until a later probe or durable observation establishes the predicate.

## Historical regression oracle

The frozen cross-framework current-basis v0.4 manifest remains byte-identical:

```text
test_id: cross-framework-current-basis-001
manifest SHA-256: 07a08496c21b31f70f6f45ef731aa5f6b2522a6fc8f67f2d0a4c2b6fceda7a3f
manifest Git blob SHA-1: 59d818a15fc7be732c97dae7d2174d8cfe9a7bab
historical observed disposition: DENY
historical raw reason: execution.authority_stale
```

The historical finding established that native currentness was intentionally left unestablished (`None`) but `_build_three_layer()` coerced those values with `bool(...)`, turning UNKNOWN into False before the canonical three-layer decision.

## Merged semantics

StegCore PR `#199` merged at `a4348d3db8e22f89acad4ae7454341968e6046d6`.

- `ExecutionBoundary` currentness/representation predicates accept `bool | None`.
- `StegGate._build_three_layer()` passes execution predicates through without boolean coercion.
- the three-layer evaluator detects unknown execution predicates before stale/invalid rules;
- unknown execution predicates return `FAIL-CLOSED / execution.probe_required` and identify the predicates requiring evidence;
- explicit `False` retains the prior denial behavior and reason codes;
- explicit `True` behavior remains unchanged.

This is not an allow-on-unknown change. It preserves fail-closed behavior while separating `not established` from `affirmatively false`.

## Validation evidence

```text
Unknown Probe Semantics Validation run 34531630404: PASS
Current-Basis Neutral Derivation Validation run 34531630392: PASS
```

The repository-wide External Evidence Interoperability run `34531630382` failed only after its pinned Governance external-evidence snapshot validation passed. All five full-suite failures were unrelated pre-existing portable-release version drift: current `VERSION` and `pyproject.toml` are `0.3.0` while `sdk/portable_release_manifest.v1.json` still declares `0.2.0`. No unknown/probe/current-basis assertion failed in that lane.

## Exact frozen longitudinal regression

StegCore PR `#200` merged at `cdb15df1c15fab5d9ca688e4d18cd47d81ebfc04`.

`Frozen v0.4 Probe Regression` run `34531908876`: PASS.
`Unknown Probe Semantics Validation` run `34531908894`: PASS.

The regression materialized the exact frozen SDK manifest from immutable SDK commit `d661bee61697024c62a48206c5d2258b22ea1413`, recomputed and matched SHA-256 `07a08496c21b31f70f6f45ef731aa5f6b2522a6fc8f67f2d0a4c2b6fceda7a3f`, and evaluated the unchanged comparison vector against the repaired merged StegCore semantics.

Observed longitudinal semantic comparison:

```text
historical run: DENY / execution.authority_stale
repaired semantic evaluation: FAIL_CLOSED / execution.probe_required
frozen manifest bytes changed: false
```

The historical August execution evidence remains unchanged and is not overwritten or reinterpreted as having produced the new result. The new regression proves that the same exact frozen test input now preserves its unestablished predicates and requests additional evidence rather than falsely asserting staleness.

## README maintenance

The root README now explicitly documents that UNKNOWN and affirmatively False are distinct execution states: UNKNOWN produces probe-required fail-closed behavior, while explicit False retains applicable DENY semantics.

## SDK distribution propagation boundary

A temporary SDK PR `#175` attempted to update the historical `1.2.0` governed-test Git pin and was closed without merge after release-line reconciliation. Mutating the frozen/historical SDK 1.2.0 dependency identity would be incorrect.

The canonical post-1.2.0 SDK trajectory is already `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`, with an SDK 1.3.0 successor source candidate and public StegCore distribution boundary. Propagating these repaired StegCore semantics into a published SDK governed-runtime dependency therefore belongs to that existing release/distribution task, not this completed semantic child.

## Completion

```text
UNKNOWN preserved through StegGate -> three-layer: PASS
unknown -> execution.probe_required: PASS
explicit false retains stale/deny behavior: PASS
exact frozen v0.4 bytes verified unchanged: PASS
exact frozen v0.4 repaired semantic result: PASS
historical evidence preserved separately: PASS
README maintenance: COMPLETE
```

## Manual work

None.
