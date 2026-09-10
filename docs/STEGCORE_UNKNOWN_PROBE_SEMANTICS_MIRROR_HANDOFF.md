# StegCore Unknown Probe Semantics Mirror Handoff

Goal Task ID: `STEGCORE-UNKNOWN-PROBE-SEMANTICS-001`
Parent Goal Task ID: `SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001`
Repository: `StegVerse-Labs/StegCore`
Status: `IMPLEMENTED_VALIDATION_IN_PROGRESS`

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

## Implemented semantics

- `ExecutionBoundary` currentness/representation predicates now accept `bool | None`.
- `StegGate._build_three_layer()` passes execution predicates through without boolean coercion.
- the three-layer evaluator detects any unknown execution predicates before stale/invalid rules;
- unknown execution predicates return `FAIL-CLOSED / execution.probe_required` and identify the predicates requiring evidence;
- explicit `False` retains the prior denial behavior and reason codes;
- explicit `True` behavior remains unchanged.

This is not an allow-on-unknown change. It preserves fail-closed behavior while separating `not established` from `affirmatively false`.

## Validation evidence so far

PR: `StegVerse-Labs/StegCore#199`

The first focused semantic run proved the implementation cases before a workflow-path typo stopped the broader step:

```text
Unknown Probe Semantics Validation run 34531334208
new semantic regression: 3 passed
failure cause: referenced nonexistent tests/test_steggate.py
implementation failure: none observed
```

After replacing that invalid target, run `34531423705` again passed the new semantic regression `3 passed`; the broader step then stopped because a second guessed filename, `tests/test_admissibility_baseline.py`, also does not exist. No semantic assertion failed. The workflow is now corrected to use the actual existing `tests/test_current_basis.py` suite only.

Existing `tests/test_current_basis.py` already requires neutral currentness to remain `None` at native derivation and does not assert the historical false-stale disposition, so no old-result assertion is being silently rewritten.

Independent existing validation:

```text
Current-Basis Neutral Derivation Validation run 34531423688: PASS
```

## Regression tests

`tests/test_unknown_probe_semantics.py` requires:

1. `actor_authority_current=None` -> `FAIL-CLOSED / execution.probe_required`;
2. `actor_authority_current=False` -> `DENY / execution.authority_stale`;
3. the neutral v0.4 vector preserves all unestablished currentness values as `None` through native derivation and now yields `FAIL_CLOSED / execution.probe_required`, never the historical false-stale reason.

## Remaining work

- obtain a fresh exact-head PASS from the corrected focused workflow;
- require the existing external-evidence interoperability lane to remain green;
- merge source remediation;
- rerun the exact frozen SDK v0.4 artifact through the updated dependency path without modifying its bytes;
- retain the new result separately from the historical run so longitudinal comparison remains reconstructable.

## Manual work

None.
