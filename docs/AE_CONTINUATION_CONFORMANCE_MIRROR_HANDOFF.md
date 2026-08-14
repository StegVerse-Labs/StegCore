# Admissible-Existence Continuation Conformance Mirror Handoff

## Source of truth

```text
organization: StegVerse-Labs
repository: StegCore
branch: feat/ae-continuation-conformance-107
active_goal_id: AE-CONTINUATION-CONFORMANCE-001
canonical_issue: #107
implementation_claim: #108
validation_claim: #109
release_task: #110
worker_registry_adoption: StegVerse-Labs/.github#123
worker_registry_claim: StegVerse-Labs/.github#124
formalism_authority: Admissible-Existence/AE + RTG + GTG + TT + STCM
canonical_runtime_authority: stegcore.steggate.evaluate_admissibility
credential_authority: TV/TVC
github_token_runtime_authority: NONE
archive_ready: false
```

This lane installs a read-only, fail-closed canonical verification procedure for HANDOFF task state and Worker Task Registry state. It verifies recently completed, current, and future work against the newest StegCore Admissible-Existence implementation without changing canonical StegGate semantics or mutating live worker claims/fences/leases.

## Required invariants

1. Capability lifecycle is `DECLARED -> STANDING -> ADMISSIBLE -> ACTIVATED`, with `SUSPENDED`, `SUPERSEDED`, and `TERMINATED` terminal/exception transitions as defined by StegCore.
2. Structural conformance can block but never widen canonical StegGate authority.
3. `ACTIVATED` always requires integration evidence and an activation proof; source, tests, files, or workflow success alone cannot infer activation.
4. Every task affecting a capability binds to a canonical capability ID and existence phase. A task that does not affect capability existence must explicitly declare `ae_impact=NONE` with a rationale.
5. Recently completed work must carry durable completion evidence and must not retain unresolved blockers or active continuation ownership unless the terminal state explicitly represents supersession/termination lineage.
6. Current unresolved work must have an owner and, when blocked/constraint-bearing, a durable continuation owner. Constraint is not terminal completion.
7. Future capability-producing work may be `DECLARED` or pre-declaration planning, but may never pre-claim `ACTIVATED` or fabricate activation evidence.
8. HANDOFF and Worker Task Registry records must reconcile task ID, goal ID, owner repository, AE impact, capability ID/phase, evidence, blockers, and continuation ownership where both surfaces carry the task.
9. Heartbeat is carrier/synchronization continuity only. Worker/task coordination is a separate control-plane capability synchronized to heartbeat observation; heartbeat cannot be declared worker executor, communication transport authority, or Master Records custody authority.
10. Master Records custody/EOL authority remains separate from worker execution and communication transport authority.
11. Credential authority is TV/TVC only. GitHub token production/runtime authority is NONE.

## Canonical procedure

The verifier consumes normalized HANDOFF and Worker Task Registry conformance records. Adoption adapters may project repository-specific formats into this normalized contract, but may not weaken its checks.

Verification order:

```text
1. schema/policy identity
2. authority invariants
3. per-task temporal class: RECENTLY_COMPLETED | CURRENT | FUTURE
4. AE impact and capability binding
5. lifecycle/evidence validity
6. ownership/continuation validity
7. HANDOFF <-> registry reconciliation
8. fail-closed result + findings
```

Canonical policy: `management/ae-continuation-conformance-policy.json`

Executable verifier: `scripts/validate_ae_continuation_conformance.py`

Deterministic tests: `tests/test_ae_continuation_conformance.py`

## Collision boundaries

- Do not modify `src/stegcore/steggate.py` or canonical StegGate evaluation semantics.
- Do not modify #104/#105-owned heartbeat/AE reconciliation surfaces in this lane.
- Do not mutate `.github` live worker claim/fence/lease/runtime state while `.github#122` owns the control-plane separation refactor.
- Do not create a second heartbeat, worker registry, scheduler, transport, custody path, or credential path.

## Completion condition

This StegCore lane is complete only after the policy, executable verifier, and tests are merged to `main` with hosted validation evidence. Ecosystem Worker Task Registry adoption remains separately owned by `.github#123/#124` until it can be integrated without colliding with `.github#122`.
