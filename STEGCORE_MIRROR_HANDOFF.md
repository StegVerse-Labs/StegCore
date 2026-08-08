# StegCore Mirror Handoff

## Source of truth

```text
Organization: StegVerse-Labs
Repository: StegCore
Canonical branch: main
Primary goal: STEGGATE-FULL-FUNCTIONAL-ACTIVATION-001
Canonical task owner: issue #68 + repository-native live observer + active originating session + Render capacity condition watch
Project state: ARCHITECTURE_RECONCILED / FULL GOVERNED EXECUTION COMPOSITION VALIDATED / HOST DEPLOYMENT BLOCKED / FULL LIVE OBSERVER + AUTOMATIC FINALIZER + CAPACITY WATCH ACTIVE
Originating chat state: ACTIVE_UNIQUE_WORK_REMAINS / DO NOT ARCHIVE UNTIL GOAL ACTIVATED
```

Read this file before changing StegCore runtime decisions, adapters, receipt bindings, live-service activation, deployment, or downstream verification. Live Git state, workflow runs/jobs, committed evidence, issues, Render observations, `data/steggate-session-context.json`, `data/steggate-architecture-reconciliation-state.json`, `management/steggate-full-functional-activation.json`, and `management/steggate-render-capacity-watch.json` supersede chat summaries.

## Active project/session goal

Make canonical StegGate fully functional and live through one authoritative admissibility-to-consequence chain. Do not stop at library/tag readiness. Do not create a parallel decision authority merely because `decision.py` is intentionally minimal. Do not archive the originating session merely because unresolved work is machine-owned. This goal remains active until the hosted service is live, required live observations pass, the activation receipt is persisted, and issue #68 is closed.

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
scripts/guard_steggate_session_continuity.py
tests/test_steggate_session_continuity.py
.github/workflows/steggate-live-observer.yml
.github/workflows/steggate-session-continuity.yml
management/steggate-render-capacity-watch.json
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

## Strongest current repository validation

StegCore Tests run `31276082614`, job `93149695844`, on head `0c1b843d3c603f0b41a64e3ba2f797fd1f2796c1` completed successfully after the active-session archive guard was restored. The prior full-suite run `31272908477`, job `93141782128`, recorded:

```text
151 passed
128 subtests passed
```

Diagnostics artifact from that full-suite run:

```text
artifact_id: 9026151563
digest: sha256:684984429c260e4dd4325d8ef42c849b75f208e8882b46ea0535c459afc539de
```

The continuity guard itself is hosted-green after reconciliation-state correction:

```text
run: 31276136526
job: 93149840636
result: SUCCESS
artifact_id: 9027042689
digest: sha256:212d757d9c155baeb6303c6b7a28fc3d31c0a95fb36d4203b8343df29b4883af
```

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
workspace: tea-d30avmndiees73bg2rjg
```

Latest explicitly inspected deploy:

```text
deploy_id: dep-d9rood9t0dsc73b92sug
head: 0c1b843d3c603f0b41a64e3ba2f797fd1f2796c1
status: build_failed
machine cause: workspace build-pipeline minutes exhausted
```

Render logs continue to state that builds are canceled before source build execution because the workspace has exhausted build-pipeline minutes for the current billing period. Render identifies workspace-plan upgrade or increased build-spend limit as immediate capacity-restoration mechanisms; neither paid action is authorized by this goal/session.

Only one connected Render workspace is available. The connected Vercel team has no StegCore project and exposes no supported project-creation mutation for this repository. Plugin discovery for an alternate supported hosting/cloud connector returned no matching installable plugin. No unsupported deployment route should be invented.

## Render capacity condition watch — ACTIVE

Durable record: `management/steggate-render-capacity-watch.json`.

A separate hourly condition watch is active against the canonical Render service. It does not treat the blocker as completion. Its required behavior is:

1. remain silent while build capacity is still exhausted;
2. when capacity becomes available, trigger a canonical deploy if none is live/in-progress;
3. inspect deployment status;
4. after a live deploy, verify `/health`, exact four-outcome `/v1/self-test`, and deterministic complete-matrix `/v1/evaluate`;
5. permit final activation reconciliation only after those checks pass.

This watch adds an execution path that can react when hosting capacity returns even if no new chat turn occurs. It has no authority to upgrade a workspace plan, increase spend, or make another paid change.

## Live observer and automatic finalizer — ACTIVE / FAIL-CLOSED

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

When and only when all three hosted checks PASS, the workflow automatically creates `data/steggate-live-activation-receipt.json`, updates context/inventory/handoff, commits the activation state, comments on issue #68, and closes #68.

Machine ownership is continuation support, not a substitute for completion. The originating session remains active until that success condition actually occurs.

## Claim and collision control

```text
task_id: STEGGATE-FULL-FUNCTIONAL-ACTIVATION-001
repository: StegVerse-Labs/StegCore
branch: main
canonical owner: issue #68 + repository-native automation + Render capacity watch + active originating session
chat claimant: ACTIVE_UNIQUE_WORK_REMAINS
project claim state: BLOCKED_HOST_ACTIVATION / MACHINE_OBSERVER_ACTIVE / CAPACITY_WATCH_ACTIVE
claim release condition: hosted health + four-outcome self-test + complete matrix evaluation PASS + activation receipt + issue #68 closed
collision boundary: no competing StegGate policy engine or canonical deployment identity
next action: capacity watch checks Render hourly; active session continues inspecting supported deployment routes and machine evidence without manufacturing authority
```

## Exact incomplete tasks

1. `FF-DEPLOY-05` — `Render/srv-d9rlic2jobas73do1q6g`: successful canonical build/deploy. State `BLOCKED + CONDITION_WATCH_ACTIVE`. Release condition: canonical deploy reaches `live`.
2. `FF-OBSERVE-06` — `.github/workflows/steggate-live-observer.yml`: obtain health/self-test/evaluate PASS. State `MACHINE_OWNED + SESSION_OBSERVED`, blocked by FF-DEPLOY-05.
3. `FF-ACTIVATE-07` — `scripts/finalize_steggate_live_activation.py` and workflow success path: persist final receipt, reconcile durable records, and close #68. State `WAITING_FOR_EVIDENCE`.

These three tasks are archival dependencies for this active session.

## Cross-repository boundaries

- Governance remains policy/evidence authority.
- `StegVerse-Labs/ara-admissibility-interop` remains canonical interop/schema owner for decision-state portability.
- `StegVerse-Labs/Continuity` remains canonical Continuity/reconstruction consumer authority.
- Existing Site, Publisher, admissibility-wiki, and StegGuardian awareness work is not evidence of live StegGate deployment and must not be mutated merely to manufacture activation.

## Archive condition

NOT SATISFIED.

```text
Current project activation tasks complete: 4/7
Incomplete: FF-DEPLOY-05, FF-OBSERVE-06, FF-ACTIVATE-07
Conversation archive allowed: false
Required before archive: full hosted PASS + activation receipt + issue #68 closed
```

The repository-native worker must fail closed if a future handoff attempts to mark this conversation archive-ready before the active StegGate functional goal itself is complete.
