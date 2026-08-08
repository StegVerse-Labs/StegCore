# StegGate Architecture Reconciliation

## Status

```text
goal_id: STEGGATE-FULL-FUNCTIONAL-ACTIVATION-001
state: COMPLETE
canonical_issue: StegVerse-Labs/StegCore#68
archive_allowed: false
reason: live deployment/runtime observation remains active
```

## Resolved architecture

The deliberately minimal `src/stegcore/decision.py` is a compatibility decision interface, not evidence that StegCore lacked the broader admissibility engine. The canonical StegGate path is now reconciled as one chain rather than parallel authorities:

```text
Governance policy/evidence artifacts
        ↓
src/stegcore/three_layer.py:evaluate_three_layer
  canonical judgment + signal/state + execution-boundary admissibility
        ↓
src/stegcore/steggate.py:evaluate_admissibility
  complete matrix normalization + pre-commit composition
  + candidate-hash-bound REVIEW when required approval is absent
        ↓
src/stegcore/commit_governance.py:coherence_gate
        ↓
src/stegcore/runtime.py:governed_execute
        ↓
src/stegcore/runtime_adapters.py:execute_adapter / execute_http
        ↓
execution observation + reconcile_effect
        ↓
Continuity/reconstruction consumers
```

`contracts/permission-admissibility-boundary.v1.json` remains a cross-cutting invariant: permission is recorded independently and never substitutes for present-tense admissibility. `docs/DECISION_STATE_RECONSTRUCTION.md` remains the reconstruction contract for decision, execution, and observed reality.

## Live-service reconciliation

The first version of `src/stegcore/steggate.py` duplicated authority/evidence/policy boolean evaluation. That implementation has been replaced.

Current classification:

| Surface | Classification | Result |
|---|---|---|
| `src/stegcore/steggate.py` | `ADAPTER_TO_EXISTING_CANONICAL_ENGINE` + `NORMALIZATION_OF_EXISTING_CANONICAL_RESULTS` + `NEW_REQUIRED_SEMANTIC_NOT_PRESENT_ELSEWHERE` | calls `evaluate_three_layer`; emits the full reconstructable matrix; composes existing capability/continuity bindings; adds candidate-hash-bound `REVIEW` only for required-but-absent human approval |
| `src/stegcore/service.py` | `ADAPTER_TO_EXISTING_CANONICAL_ENGINE` | HTTP transport only; `/v1/evaluate` routes through the reconciled composition; no arbitrary external mutation endpoint |
| `tests/test_steggate_service.py` | validation | proves canonical binding and four-outcome normalization |

The service therefore no longer claims an independent policy engine. Canonical ALLOW/DENY/FAIL_CLOSED authority comes from `evaluate_three_layer`; known canonical denial outranks REVIEW, canonical FAIL-CLOSED remains epistemically distinct, and supplemental runtime-binding uncertainty fails closed.

## Full-matrix preservation

The normalized matrix preserves material predicates even though the canonical three-layer evaluator can terminate on the first governing failure. The matrix is reconstruction evidence, not an alternative source of authority. It records the state of judgment, signal/state integrity, execution-boundary facts, capability, verified-continuity input, approval binding, and permission presence.

The result also binds:

- candidate hash;
- canonical three-layer request hash;
- canonical three-layer receipt hash;
- final decision-state hash;
- permission/admissibility separation;
- `continuity_receipt_minted=false`;
- `external_execution_performed=false` for the evaluation-only service.

## Validation

Hosted repository validation after reconciliation:

```text
workflow: StegCore Tests
run_id: 31270227248
job_id: 93134793274
head_sha: 5d79a86517632a6a0cda295f3f1d63280477aff5
result: PASS
140 passed, 127 subtests passed
artifact_id: 9025372171
artifact_digest: sha256:1de4068a06e0271d6e6077fc0b8d4e33520ac3153c21a0291018064abf522a9c
```

## Remaining activation work

Architecture reconciliation is no longer a blocker. The active blocker is hosted runtime activation/observation.

Render service `srv-d9rlic2jobas73do1q6g` exists but the attempted build was canceled because the workspace exhausted build-pipeline minutes. The next executable action is to deploy the same canonical `main` service through an available authorized hosting control plane, or allow the existing Render service to deploy once capacity returns, then directly observe:

1. `/health` healthy and canonical-three-layer-bound;
2. `/v1/self-test` PASS for ALLOW/DENY/REVIEW/FAIL_CLOSED;
3. `/v1/evaluate` returning a complete matrix plus canonical three-layer and decision-state hashes.

## Session-continuity guard

Canonical machine context: `data/steggate-session-context.json`.
Architecture state: `data/steggate-architecture-reconciliation-state.json`.
Worker: `scripts/guard_steggate_session_continuity.py`.
Workflow: `.github/workflows/steggate-session-continuity.yml`.

The active functional goal is not archive-ready until hosted activation and observations are complete or genuinely transferred without losing execution context.
