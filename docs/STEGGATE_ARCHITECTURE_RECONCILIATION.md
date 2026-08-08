# StegGate Architecture Reconciliation

## Purpose

This record prevents loss of architectural context while `STEGGATE-FULL-FUNCTIONAL-ACTIVATION-001` remains active. It is a worker-consumed continuation record, not a replacement decision engine.

## Verified existing canonical layers

1. `src/stegcore/decision.py`
   - intentionally documents itself as a minimal deterministic decision interface;
   - uses shape references only and explicitly says it is not a full policy engine;
   - therefore must not be treated, by itself, as evidence that broader StegGate capability is missing.

2. `src/stegcore/three_layer.py`
   - existing deterministic three-layer admissibility runtime;
   - evaluates judgment conditions, signal admission/state integrity, and execution-boundary currency/recoverability;
   - returns `ALLOW`, `DENY`, or `FAIL-CLOSED`;
   - preserves policy/delegation/evidence references, reference-state hashes, findings, and a deterministic evidence receipt;
   - does not mint Continuity receipts.

3. `contracts/permission-admissibility-boundary.v1.json` plus `docs/PERMISSION_ADMISSIBILITY_MIRROR_HANDOFF.md`
   - canonical permission/admissibility semantic invariant;
   - permission is independent of present-tense admissibility;
   - successful execution does not prove authority or admissibility.

4. `src/stegcore/commit_governance.py`
   - canonical commit-coherence gate after admissibility;
   - preserves authority, denial reachability, governed continuation, capability binding, and receipt chaining.

5. `src/stegcore/runtime.py#governed_execute`
   - production mutation boundary;
   - mutation callback is unreachable unless the decision layer and coherence gate permit execution.

6. `src/stegcore/runtime_adapters.py`
   - canonical adapter convergence surface for supported caller classes.

7. `docs/DECISION_STATE_RECONSTRUCTION.md` and Continuity interop
   - complete decision state, including non-execution and reconciliation, is part of reconstructable reality.

## Provisional live-service additions

The files below were added during live functional activation and MUST remain provisional until this reconciliation is complete:

- `src/stegcore/steggate.py`
- `src/stegcore/service.py`
- `tests/test_steggate_service.py`
- `docs/STEGGATE_LIVE_SERVICE.md`

Current classification: `PROVISIONAL_ADAPTER_OR_DUPLICATION_RISK`.

The new evaluator overlaps existing three-layer admissibility semantics. It additionally models `REVIEW` and exposes a full predicate matrix. That does not yet establish that it should become a separate authoritative decision engine.

## Required reconciliation outcome

Before further feature expansion or live activation, classify each new live-service responsibility as exactly one of:

- `ADAPTER_TO_EXISTING_CANONICAL_ENGINE`
- `NORMALIZATION_OF_EXISTING_CANONICAL_RESULTS`
- `NEW_REQUIRED_SEMANTIC_NOT_PRESENT_ELSEWHERE`
- `DUPLICATE_REMOVE_OR_REFACTOR`

The preferred architecture is one canonical admissibility authority with service/API normalization around it, not parallel engines that can diverge.

## Required call graph to establish

```text
Governance policy/evidence artifacts
        ↓
existing StegCore admissibility runtime(s)
        ↓
complete decision-state normalization
        ↓
commit coherence
        ↓
governed_execute mutation boundary
        ↓
execution observation
        ↓
Continuity/reconstruction + reconciliation
```

The live service must expose this canonical chain without acquiring mutation, Continuity, publication, deployment, or external legal authority.

## Archive guard

While this reconciliation is incomplete:

- `archive_allowed=false`;
- completion of a bounded subtask does not make the active functional goal archive-ready;
- historical context loss is a validation failure;
- the worker must emit `DO_NOT_ARCHIVE` and the exact next action.

Canonical machine context: `data/steggate-session-context.json`.
Worker: `scripts/guard_steggate_session_continuity.py`.
Workflow: `.github/workflows/steggate-session-continuity.yml`.
Canonical activation issue: `StegVerse-Labs/StegCore#68`.
