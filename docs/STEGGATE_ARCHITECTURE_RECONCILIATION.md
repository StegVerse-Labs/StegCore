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

The deliberately minimal `src/stegcore/decision.py` is a compatibility decision interface, not evidence that StegCore lacked the broader admissibility engine. The canonical StegGate path is one chain rather than parallel authorities:

```text
Governance policy/evidence artifacts
        ↓
src/stegcore/three_layer.py:evaluate_three_layer
  canonical judgment + signal/state + execution-boundary admissibility
        ↓
src/stegcore/steggate.py:evaluate_admissibility
  complete matrix normalization + capability/continuity composition
  + candidate-hash-bound REVIEW when required approval is absent
        ↓
src/stegcore/steggate_runtime.py:governed_steggate_execute
        ↓
src/stegcore/commit_governance.py:coherence_gate
        ↓
injected mutation callback at governed commit boundary
        ↓
execution observation + runtime_adapters reconciliation semantics
        ↓
Continuity/reconstruction consumers
```

`contracts/permission-admissibility-boundary.v1.json` remains a cross-cutting invariant: permission is recorded independently and never substitutes for present-tense admissibility. `docs/DECISION_STATE_RECONSTRUCTION.md` remains the reconstruction contract for decision, execution, and observed reality.

## Reconciliation outcome

The first version of `src/stegcore/steggate.py` duplicated authority/evidence/policy boolean evaluation. That implementation was replaced. Canonical ALLOW/DENY/FAIL_CLOSED authority now derives from `evaluate_three_layer`; known canonical denial outranks REVIEW, canonical FAIL-CLOSED remains epistemically distinct, and supplemental runtime-binding uncertainty fails closed.

Current classification:

| Surface | Classification | Result |
|---|---|---|
| `src/stegcore/steggate.py` | `ADAPTER_TO_EXISTING_CANONICAL_ENGINE` + `NORMALIZATION_OF_EXISTING_CANONICAL_RESULTS` + `NEW_REQUIRED_SEMANTIC_NOT_PRESENT_ELSEWHERE` | calls `evaluate_three_layer`; emits the full reconstructable matrix; composes existing capability/continuity bindings; adds candidate-hash-bound `REVIEW` only for required-but-absent human approval |
| `src/stegcore/steggate_runtime.py` | `ADAPTER_TO_EXISTING_CANONICAL_ENGINE` + `NEW_REQUIRED_INTEGRATION` | binds the full StegGate decision state to the existing coherence gate and executor; the executor is unreachable for non-ALLOW, coherence denial, or missing commit authority; successful coherence receipts bind the full decision-state hash |
| `src/stegcore/service.py` | `ADAPTER_TO_EXISTING_CANONICAL_ENGINE` | HTTP evaluation transport only; no arbitrary remote mutation endpoint |
| `tests/test_steggate_service.py` | validation | proves canonical three-layer binding and four-outcome normalization |
| `tests/test_steggate_runtime.py` | integration validation | proves non-ALLOW/coherence-denial executor unreachability and ALLOW+coherence execution |

`src/stegcore/runtime.py#governed_execute` remains an existing minimal-interface runtime surface for compatibility. It must not be used to infer that `decision.py` is the full StegGate authority surface. The full StegGate consequence path is the explicit `steggate_runtime` composition above.

## Full-matrix preservation

The normalized matrix preserves material predicates even though the canonical three-layer evaluator can terminate on the first governing failure. The matrix is reconstruction evidence, not an alternative source of authority. It records judgment, signal/state integrity, execution-boundary facts, capability, verified-continuity input, approval binding, and permission presence.

The result binds:

- candidate hash;
- canonical three-layer request hash;
- canonical three-layer receipt hash;
- final decision-state hash;
- permission/admissibility separation;
- `continuity_receipt_minted=false`;
- `external_execution_performed=false` for the evaluation-only HTTP surface.

The governed consequence composition additionally binds the final `decision_state_hash` into the finalized coherence receipt before the executor result is recorded.

## Validation

Strongest hosted repository validation after full decision-to-commit integration:

```text
workflow: StegCore Tests
run_id: 31270401058
job_id: 93135227329
head_sha: a274527d501138f25ecf4dbfec9fda62eafa154d
result: PASS
148 passed, 127 subtests passed
artifact_id: 9025421552
artifact_digest: sha256:4cce13a6ec682d09d9f84d3ca739f297bc942290112d2baedabeafe98cb27220
```

## Hosted activation automation

The repository-native observer is:

```text
scripts/observe_steggate_live_service.py
tests/test_steggate_live_observer.py
.github/workflows/steggate-live-observer.yml
```

It runs hourly and on relevant pushes. It fails closed until all of these are observed from the canonical service:

1. `/health` healthy and canonical-three-layer-bound;
2. `/v1/self-test` exact ALLOW/DENY/REVIEW/FAIL_CLOSED PASS;
3. deterministic `POST /v1/evaluate` returns ALLOW, complete required matrix predicates, all candidate/canonical-three-layer/decision-state hashes, permission/admissibility separation, no Continuity mint authority, and no external execution from the evaluation endpoint.

The first observer run before POST-evaluate was added was `31270353764`, job `93135108552`; observer tests passed but health and self-test both timed out because the Render service has no successful build. Artifact `9025414196`, digest `sha256:2708b4d4d99763903c85f03eba2402d0e6bf7e932c15979e95f7e339a70f2e5a` preserves that blocked state.

## Remaining activation work

Architecture reconciliation and repository execution integration are no longer blockers. The active blocker is hosted runtime activation.

Render service `srv-d9rlic2jobas73do1q6g` exists but every attempted auto-deploy is canceled because the workspace has exhausted build-pipeline minutes. A connected Vercel team was inspected, but no StegCore project exists and the currently exposed deployment connector does not provide a supported project-creation/deploy invocation for this repository.

The machine-observable release condition is therefore: a canonical hosted deployment becomes live, after which the already-active observer must produce a single PASS receipt containing successful health, four-outcome self-test, and complete hosted evaluation evidence.

## Session-continuity guard

Canonical machine context: `data/steggate-session-context.json`.
Architecture state: `data/steggate-architecture-reconciliation-state.json`.
Active execution inventory: `management/steggate-full-functional-activation.json`.
Worker: `scripts/guard_steggate_session_continuity.py`.
Workflow: `.github/workflows/steggate-session-continuity.yml`.

The active functional goal is not archive-ready until hosted activation and observations are complete.
