# StegCore Mirror Handoff

## Source of truth

```text
Organization: StegVerse-Labs
Repository: StegCore
Canonical branch: main
Primary goal: STEGGATE-FULL-FUNCTIONAL-ACTIVATION-001
Canonical task owner: issue #68 + repository-native live observer
Project state: ARCHITECTURE_RECONCILED / FULL GOVERNED EXECUTION COMPOSITION VALIDATED / HOST DEPLOYMENT BLOCKED / FULL LIVE OBSERVER + AUTOMATIC FINALIZER ACTIVE
Originating chat state: MERGED INTO CANONICAL WORKSTREAM / ARCHIVE SAFE
```

Read this file before changing StegCore runtime decisions, adapters, receipt bindings, live-service activation, deployment, or downstream verification. Live Git state, workflow runs/jobs, committed evidence, issues, Render observations, `data/steggate-session-context.json`, `data/steggate-architecture-reconciliation-state.json`, and `management/steggate-full-functional-activation.json` supersede chat summaries.

## Active project goal

Make canonical StegGate fully functional and live through one authoritative admissibility-to-consequence chain. Do not stop at library/tag readiness. Do not create a parallel decision authority merely because `decision.py` is intentionally minimal. Project activation remains incomplete until hosted runtime observations satisfy the release conditions below.

Conversation archival is a separate question from project activation. The originating session may be archived once its unique knowledge and execution responsibility are durably transferred. That transfer is now complete: unresolved work is machine-owned and has explicit release conditions and automatic finalization.

## Architecture reconciliation — COMPLETE

Canonical record: `docs/STEGGATE_ARCHITECTURE_RECONCILIATION.md`.
Machine state: `data/steggate-architecture-reconciliation-state.json`.

Resolved call graph:

```text
Governance policy/evidence artifacts
        ↓
src/stegcore/three_layer.py:evaluate_three_layer
        ↓
src/stegcore/steggate.py:evaluate_admissibility
  complete matrix normalization + REVIEW composition
        ↓
src/stegcore/steggate_runtime.py:governed_steggate_execute
        ↓
src/stegcore/commit_governance.py:coherence_gate
        ↓
injected mutation callback at governed commit boundary
        ↓
execution observation / runtime_adapters reconciliation semantics
        ↓
Continuity/reconstruction consumers
```

Architectural facts:

1. `src/stegcore/decision.py` is deliberately minimal and remains a compatibility interface. Its minimal scope is not evidence that a full engine is absent.
2. `src/stegcore/three_layer.py` is the canonical core evaluator for judgment conditions, signal/reference-state integrity, and execution-boundary authority/policy/delegation/evidence/recoverability.
3. `contracts/permission-admissibility-boundary.v1.json` keeps permission distinct from present-tense admissibility.
4. `src/stegcore/steggate.py` calls the canonical three-layer evaluator, normalizes the complete material matrix for reconstruction, composes existing capability/verified-continuity bindings, and adds candidate-hash-bound human-approval `REVIEW` semantics. It is not a parallel policy engine.
5. `src/stegcore/steggate_runtime.py` binds the full decision state to existing commit coherence. A mutation callback is unreachable for `DENY`, `REVIEW`, `FAIL_CLOSED`, coherence denial, or missing commit authority.
6. An `ALLOW` plus independent coherence `ALLOW` may invoke the injected executor; its finalized coherence receipt binds the StegGate `decision_state_hash`.
7. `src/stegcore/runtime.py#governed_execute` remains a compatibility surface; it is not used as proof of the full StegGate evaluation path.
8. `src/stegcore/runtime_adapters.py` remains the existing caller-binding and later effect-reconciliation semantic surface.
9. Full decision state, including non-occurrence and divergence, remains reconstructable reality under `docs/DECISION_STATE_RECONSTRUCTION.md` and Continuity contracts.

## Implemented functional surfaces

```text
src/stegcore/steggate.py
src/stegcore/steggate_runtime.py
src/stegcore/service.py
tests/test_steggate_service.py
tests/test_steggate_runtime.py
scripts/observe_steggate_live_service.py
tests/test_steggate_live_observer.py
scripts/finalize_steggate_live_activation.py
tests/test_finalize_steggate_live_activation.py
.github/workflows/steggate-live-observer.yml
```

HTTP evaluation surface:

```text
GET  /
GET  /health
GET  /v1/capabilities
GET  /v1/self-test
POST /v1/evaluate
```

The public HTTP service deliberately exposes evaluation only. It does not expose an arbitrary remote mutation callback or acquire deployment, Continuity, publication, legal, custody, payment, or external-system authority.

## Strongest completed runtime validation

StegCore Tests run `31270401058`, job `93135227329`, on head `a274527d501138f25ecf4dbfec9fda62eafa154d` completed:

```text
148 passed
127 subtests passed
```

Diagnostics artifact:

```text
artifact_id: 9025421552
digest: sha256:4cce13a6ec682d09d9f84d3ca739f297bc942290112d2baedabeafe98cb27220
```

The automatic activation-finalizer semantics are separately exercised by the live-observer workflow. Run `31272908461` passed the `Validate observer and finalizer semantics` step before entering the hosted network observation.

## Canonical hosted service — CREATED, NOT LIVE

Render service:

```text
name: steggate-core
service_id: srv-d9rlic2jobas73do1q6g
origin: https://steggate-core.onrender.com
repo: StegVerse-Labs/StegCore
branch: main
auto_deploy: yes
plan: free
region: oregon
```

Render continues to reject canonical `main` builds because the workspace build-pipeline minute allowance is exhausted. Latest explicitly inspected deploy:

```text
deploy_id: dep-d9rmt70u01pc73dkt8hg
head: 9c70c7861ae000386c53c93891180d1d52060678
status: build_failed
machine cause: workspace build-pipeline minutes exhausted
```

This remains a hosting-capacity blocker, not source/test evidence of failure.

## Live observer and automatic finalizer — MACHINE OWNED

Canonical automation:

```text
.github/workflows/steggate-live-observer.yml
scripts/observe_steggate_live_service.py
scripts/finalize_steggate_live_activation.py
```

Trigger: relevant pushes, manual recovery dispatch, and hourly schedule at minute 23.

Every observation cycle requires:

1. `GET /health` -> `healthy` and `canonical_three_layer_bound=true`;
2. `GET /v1/self-test` -> `PASS` with exact ALLOW/DENY/REVIEW/FAIL_CLOSED mapping;
3. deterministic `POST /v1/evaluate` -> `ALLOW`, complete required predicate matrix, `candidate_hash`, `canonical_three_layer_request_hash`, `canonical_three_layer_receipt_hash`, `decision_state_hash`, permission/admissibility separation, and explicit absence of execution/Continuity-minting authority.

The workflow persists every observation artifact and deliberately fails while the target is unavailable or incomplete.

When and only when all three hosted checks PASS, the same workflow automatically:

```text
runs scripts/finalize_steggate_live_activation.py
creates data/steggate-live-activation-receipt.json
updates data/steggate-session-context.json
updates management/steggate-full-functional-activation.json
updates this STEGCORE_MIRROR_HANDOFF.md
commits and pushes the canonical activation state
comments on StegVerse-Labs/StegCore#68
closes issue #68 as completed
```

The success path therefore does not require this chat session or another manual polling session.

## Claim and collision control

```text
task_id: STEGGATE-FULL-FUNCTIONAL-ACTIVATION-001
repository: StegVerse-Labs/StegCore
branch: main
canonical owner: issue #68 + .github/workflows/steggate-live-observer.yml
chat claimant: RELEASED / MERGED INTO CANONICAL WORKSTREAM
project claim state: MACHINE_OWNED_BLOCKED_HOST_ACTIVATION
claim release condition: hosted health + four-outcome self-test + complete matrix evaluation PASS
collision boundary: no competing StegGate policy engine or canonical deployment identity
next action after release: automatic finalizer persists receipt and closes #68
```

## Exact incomplete project tasks

1. `FF-DEPLOY-05` — `Render/srv-d9rlic2jobas73do1q6g`: successful canonical build/deploy. Owner: Render auto-deploy plus repository automation. State: `MACHINE_OWNED_BLOCKED`. Release condition: canonical deploy reaches `live`.
2. `FF-OBSERVE-06` — `.github/workflows/steggate-live-observer.yml`: obtain health/self-test/evaluate PASS. Owner: repository automation. State: `MACHINE_OWNED`.
3. `FF-ACTIVATE-07` — `scripts/finalize_steggate_live_activation.py` and workflow success path: persist final receipt, reconcile durable records, and close #68. Owner: repository automation. State: `MACHINE_OWNED_WAITING_FOR_EVIDENCE`.

No unresolved task is owned by this conversation. There are no unnamed external or manual tasks.

## Cross-repository boundaries

- Governance remains policy/evidence authority.
- `StegVerse-Labs/ara-admissibility-interop` remains canonical interop/schema owner for decision-state portability.
- `StegVerse-Labs/Continuity` remains canonical Continuity/reconstruction consumer authority.
- Existing Site, Publisher, admissibility-wiki, and StegGuardian awareness work is not evidence of live StegGate deployment and must not be mutated merely to manufacture activation.

## Session consolidation

The complete originating-session requirement set has been transferred to this handoff, `management/steggate-full-functional-activation.json`, issue #68, the Render service, the live observer, and the automatic finalizer. The earlier `management/steggate-runtime-session-consolidation-2026-08-08.json` remains authoritative only for its prior bounded v0.1.0/tag goal.

```text
MERGED INTO: StegVerse-Labs/StegCore/STEGCORE_MIRROR_HANDOFF.md
Canonical task: StegVerse-Labs/StegCore#68
Machine continuation: .github/workflows/steggate-live-observer.yml
Automatic finalization: scripts/finalize_steggate_live_activation.py
Conversation-specific roles remaining: 0
Conversation archival: SAFE
Project activation: INCOMPLETE / FAIL-CLOSED
```

Deleting or archiving the originating conversation does not impair future execution: all remaining project work is durably represented, machine-owned, observable, and automatically finalized when its release condition becomes true.
