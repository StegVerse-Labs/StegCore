# StegCore Mirror Handoff

## Source of truth

```text
Organization: StegVerse-Labs
Repository: StegCore
Canonical branch: main
Primary goal: STEGGATE-FULL-FUNCTIONAL-ACTIVATION-001
Canonical task owner: issue #68
State: ARCHITECTURE_RECONCILED / FULL GOVERNED EXECUTION COMPOSITION VALIDATED / HOST DEPLOYMENT BLOCKED / LIVE OBSERVER ACTIVE
```

Read this file before changing StegCore runtime decisions, adapters, receipt bindings, live-service activation, deployment, or downstream verification. Live Git state, workflow runs/jobs, committed evidence, issues, Render observations, `data/steggate-session-context.json`, and `data/steggate-architecture-reconciliation-state.json` supersede chat summaries.

## Active goal

Make canonical StegGate fully functional and live through one authoritative admissibility-to-consequence chain. Do not stop at library/tag readiness. Do not create a parallel decision authority merely because `decision.py` is intentionally minimal. Do not mark this active goal archive-ready until hosted runtime observations satisfy the release conditions below.

## Historical-context guard

The project has a repository-native continuity worker because premature session archival previously removed useful architecture context.

Authoritative worker surfaces:

```text
data/steggate-session-context.json
data/steggate-architecture-reconciliation-state.json
scripts/guard_steggate_session_continuity.py
tests/test_steggate_session_continuity.py
.github/workflows/steggate-session-continuity.yml
```

The worker fails closed if required architecture distinctions, the four dispositions, the three reality planes, owner/next-action state, or archive prerequisites disappear. Active work forces `archive_allowed=false`.

Hosted worker evidence includes run `31267562113`, job `93128078146`, artifact `9024610226`, digest `sha256:01a31b811df5cb58a4bbdec30ccbd2f72d8c9d707011812d7adb7efe8e4786bc`.

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
4. `src/stegcore/steggate.py` no longer contains an independent boolean policy engine. It calls the canonical three-layer evaluator, normalizes the complete material matrix for reconstruction, composes existing capability/verified-continuity bindings, and adds only the required candidate-hash-bound human-approval `REVIEW` semantic.
5. `src/stegcore/steggate_runtime.py` binds that full decision state to existing commit coherence. A mutation callback is unreachable for `DENY`, `REVIEW`, `FAIL_CLOSED`, coherence denial, or missing commit authority.
6. An `ALLOW` plus independent coherence `ALLOW` may invoke the injected executor; its finalized coherence receipt binds the StegGate `decision_state_hash`.
7. `src/stegcore/runtime.py#governed_execute` remains an existing minimal-interface runtime surface for compatibility; it is not used as evidence that the full StegGate evaluation is complete.
8. `src/stegcore/runtime_adapters.py` remains the canonical existing caller-binding and later effect-reconciliation semantic surface.
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

## Strongest current repository validation

After full decision-to-commit integration, StegCore Tests run `31270401058`, job `93135227329`, on head `a274527d501138f25ecf4dbfec9fda62eafa154d` completed the substantive test path successfully:

```text
148 passed
127 subtests passed
```

Diagnostics artifact:

```text
artifact_id: 9025421552
digest: sha256:4cce13a6ec682d09d9f84d3ca739f297bc942290112d2baedabeafe98cb27220
```

The preceding reconciled service-only validation run `31270227248`, job `93134793274`, passed `140 tests + 127 subtests`; it is superseded by the stronger runtime-integrated validation above.

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

Render has attempted every new `main` commit automatically, but the builds are canceled before source build execution because the workspace has exhausted its build-pipeline minutes for the current billing period. Latest observed failed deploy at this handoff update:

```text
deploy_id: dep-d9rmnub7uimc73b5u58g
head: 43c5195097d5b9e8797a86d83b8977d066e4d609
status: build_failed
machine cause: workspace build pipeline minutes exhausted
```

This is an account-level hosting-capacity blocker, not a source/test failure.

## Live observer — ACTIVE / FAIL-CLOSED

The repository now owns the repeated deployment/runtime observation instead of relying on a chat session:

```text
scripts/observe_steggate_live_service.py
tests/test_steggate_live_observer.py
.github/workflows/steggate-live-observer.yml
```

Trigger: relevant pushes, manual recovery dispatch, and hourly schedule at minute 23.

The observer requires:

- `/health` -> `healthy` and `canonical_three_layer_bound=true`;
- `/v1/self-test` -> `PASS` with exact ALLOW/DENY/REVIEW/FAIL_CLOSED mapping;
- then `/v1/evaluate` must be exercised and complete matrix/hash evidence retained before activation completion.

First hosted observer evidence:

```text
run_id: 31270353764
job_id: 93135108552
observer unit tests: 3 passed
health: TIMEOUTERROR
self_test: TIMEOUTERROR
state: BLOCKED
artifact_id: 9025414196
artifact_digest: sha256:2708b4d4d99763903c85f03eba2402d0e6bf7e932c15979e95f7e339a70f2e5a
```

The workflow intentionally concludes failure while the service is unavailable. That is the required fail-closed activation state, not a worker defect.

## Alternative hosting investigation

The connected Vercel control plane was inspected. The available team contains projects `site`, `stegverse-scw`, `scw`, and `steg-verse-scw`; no StegCore/StegGate project exists. The exposed deployment action requires arguments not exposed in its connector schema and no project-creation action is available, so no supported Vercel deployment mutation can presently be performed from this control plane without inventing unsupported parameters. Do not represent Vercel as deployed.

Legacy Render `steggate-api` and `steggate-api-tp4t` remain sourced from `StegGhost/entity-sandbox-runner`; they are not canonical StegCore deployment evidence and must not be repurposed as if they were.

## Claim and collision control

```text
task_id: STEGGATE-FULL-FUNCTIONAL-ACTIVATION-001
originating_goal: make StegGate actually functional and live while preserving complete admissibility reality
repository: StegVerse-Labs/StegCore
branch: main
surfaces: reconciled evaluator, governed execution composition, HTTP service, context worker, live observer, Render service
claimant: this activation workstream / issue #68
role: implementation + validation + deployment activation + observation
claim_state: BLOCKED_HOST_ACTIVATION / MACHINE_OBSERVER_ACTIVE
claim_created: 2026-08-08
claim_release_condition: live service + health + four-outcome self-test + real evaluate evidence
expected_evidence: hosted deploy ID, health response, self-test response, evaluate matrix/hashes, persisted receipt
collision_boundary: no competing StegGate policy engine or canonical deployment identity
next_task_after_release: integration/consumer activation only if separately required by the live result
```

## Exact incomplete tasks

1. `FF-DEPLOY-01` — `Render/srv-d9rlic2jobas73do1q6g`: obtain a successful build/deploy of current canonical `main`. Owner: Render hosting control plane; state `BLOCKED`. Release condition: a deploy reaches `live`.
2. `FF-OBSERVE-02` — `.github/workflows/steggate-live-observer.yml`: obtain `/health` and `/v1/self-test` PASS from the canonical origin. Owner: repository automation; state `MACHINE_OWNED/BLOCKED_BY_FF-DEPLOY-01`.
3. `FF-EVALUATE-03` — canonical origin `/v1/evaluate`: execute a real evaluation after service is live and persist the complete matrix, canonical three-layer request/receipt hashes, candidate hash, and decision-state hash. Owner: issue #68 activation lane; state `WAITING_FOR_EVIDENCE` dependent on FF-OBSERVE-02.
4. `FF-HANDOFF-04` — this file + `data/steggate-session-context.json`: change `archive_allowed` only after the three items above are directly verified. Owner: context worker/issue #68.

There are no unnamed external tasks. The only unresolved dependency is the inability of the currently connected hosting surfaces to produce a live canonical deployment: Render rejects builds for exhausted build minutes and the Vercel connector presently exposes no usable StegCore project-creation/deployment path.

## Cross-repository boundaries

- Governance remains policy/evidence authority.
- `StegVerse-Labs/ara-admissibility-interop` remains canonical interop/schema owner for decision-state portability.
- `StegVerse-Labs/Continuity` remains canonical Continuity/reconstruction consumer authority.
- Existing Site, Publisher, admissibility-wiki, and StegGuardian awareness work is not evidence of live StegGate deployment and should not be mutated merely to manufacture completion.

## Session consolidation

The earlier `management/steggate-runtime-session-consolidation-2026-08-08.json` accurately closed the prior bounded v0.1.0/tag workstream, but its `ARCHIVE_READY` disposition does **not** govern this later functional-activation goal. The active successor inventory is `management/steggate-full-functional-activation.json`.

## Archive condition

NOT SATISFIED.

Architecture reconciliation is complete, duplicate decision authority was removed, full StegGate decision-to-coherence execution composition is implemented and hosted-CI validated, and repository-native context/live observers are active. However the canonical hosted service has never completed a build and the live health/self-test/evaluate observations required by issue #68 do not exist. This session must not be marked archive-ready while that active functional goal remains incomplete.
