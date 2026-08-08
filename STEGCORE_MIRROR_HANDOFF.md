# StegCore Mirror Handoff

## Source of truth

```text
Organization: StegVerse-Labs
Repository: StegCore
Canonical branch: main
Primary goal: STEGGATE-FULL-FUNCTIONAL-ACTIVATION-001
Canonical task owner: issue #68
State: ARCHITECTURE_RECONCILIATION_IN_PROGRESS / LIVE_SERVICE_PROVISIONAL / HOST_DEPLOYMENT_BLOCKED
```

Read this file before changing StegCore runtime decisions, adapters, receipt bindings, live-service activation, deployment, or downstream verification. Live Git state, workflow runs/jobs, committed evidence, issues, Render observations, and `data/steggate-session-context.json` supersede chat summaries.

## Active goal

Make canonical StegGate directly usable as a live service through the existing authoritative admissibility/runtime chain. Do not stop at library/tag readiness, and do not create a parallel decision authority merely because a deliberately minimal interface exists.

## Architectural invariants

1. `src/stegcore/runtime.py#governed_execute` remains the production mutation boundary.
2. Transport never creates authority; mutation remains unreachable until admissibility and commit coherence permit it.
3. StegCore consumes already-verified continuity references and does not verify signatures or mint Continuity receipts.
4. ALLOW, DENY, REVIEW, FAIL_CLOSED, coherence denial, execution failure, non-execution, observation, and reconciliation remain reconstructable.
5. Decision reality, execution reality, and observed reality remain distinct.
6. Live evaluation is not arbitrary remote mutation authority.
7. `src/stegcore/decision.py` is intentionally a minimal interface; that describes interface scope, not resource economy, and does not prove that the repository lacks a broader admissibility engine.
8. Historical/session context required to distinguish interfaces, engines, authority boundaries, and prior design decisions must be preserved durably before any archival determination.

## Architecture reconciliation — ACTIVE

Canonical record: `docs/STEGGATE_ARCHITECTURE_RECONCILIATION.md`.

Verified existing layers:

```text
src/stegcore/decision.py                       minimal deterministic interface
src/stegcore/three_layer.py                    existing three-layer admissibility runtime
contracts/permission-admissibility-boundary.v1.json
                                                 permission/admissibility invariant
src/stegcore/commit_governance.py              commit-coherence gate
src/stegcore/runtime.py#governed_execute       production mutation boundary
src/stegcore/runtime_adapters.py               caller convergence
 docs/DECISION_STATE_RECONSTRUCTION.md          decision/execution/observation reconstruction
```

`src/stegcore/three_layer.py` already evaluates judgment conditions, signal admission/reference-state integrity, and execution-boundary authority/policy/delegation/evidence/recoverability. It returns ALLOW, DENY, or FAIL-CLOSED with deterministic findings and an evidence receipt. Therefore the new live evaluator must not be assumed canonical merely because `decision.py` is minimal.

The live-service additions are currently classified `PROVISIONAL_ADAPTER_OR_DUPLICATION_RISK` until each responsibility is classified as adapter, normalization, genuinely missing semantic, or duplicate/refactor target.

## Session-context worker — ACTIVE / FAIL-CLOSED

The project now has a repository-native worker specifically to prevent architectural details from being lost through premature session archival:

```text
data/steggate-session-context.json
scripts/guard_steggate_session_continuity.py
tests/test_steggate_session_continuity.py
.github/workflows/steggate-session-continuity.yml
```

Worker contract:

- preserves the active functional goal, canonical owner, architectural distinctions, provisional files, deployment state, exact next action, and machine-observable release conditions;
- treats loss of required historical context as a validation failure;
- fails closed if the anti-duplication context, four required dispositions, three reality planes, owner, next action, or archive prerequisites disappear;
- forces `archive_allowed=false` while `session_state=ACTIVE_UNIQUE_WORK_REMAINS`;
- runs on relevant pushes and hourly schedule and uploads a continuity receipt;
- does not grant implementation, deployment, publication, Continuity, or external execution authority.

This worker is part of the execution process, not documentation-only guidance.

## Completed prior chain

Governed runtime adapters, decision-state reconstruction, evidence persistence, downstream reconciliation, Governance freshness, independent release-policy evaluation, authorized annotated tag `v0.1.0`, and post-tag awareness were completed before this goal. Issues #21, #23, #37, and #64 are closed for that chain.

## Live service implementation — PROVISIONAL / REPOSITORY VALIDATED

Canonical issue: `StegVerse-Labs/StegCore#68`.

Installed on `main`:

```text
src/stegcore/steggate.py
src/stegcore/service.py
tests/test_steggate_service.py
pyproject.toml
docs/STEGGATE_LIVE_SERVICE.md
```

The service exposes:

```text
GET /health
GET /v1/capabilities
GET /v1/self-test
POST /v1/evaluate
```

The provisional evaluator returns a complete predicate matrix and preserves four dispositions: `ALLOW`, `DENY`, `REVIEW`, `FAIL_CLOSED`. Critical unknown evidence fails closed. Human approval is candidate-hash bound. Candidate and decision-state hashes are deterministic canonical SHA-256 values. No arbitrary remote mutation endpoint is exposed.

These semantics remain subject to architecture reconciliation against the existing three-layer runtime and permission/admissibility contract before they can be called the canonical StegGate decision engine.

## Repository validation

Head `7cc4feb5311a3453e7f60e38109a37c9538a795b` completed StegCore Tests successfully in run `31266956563` and Test Readiness successfully in run `31266956537`. Packaging hardening was committed at `522b10ebbe2ebca1dec1a93366fcecf42d231047` so setuptools discovers only the canonical `src/stegcore` package for hosted installation.

The session-continuity worker and architecture reconciliation records were subsequently installed; their dedicated workflow receipt is required as part of the active reconciliation evidence.

## Hosted activation — BLOCKED BY MACHINE-OBSERVED RENDER QUOTA

A canonical Render service was actually created in the confirmed workspace:

```text
service: steggate-core
service id: srv-d9rlic2jobas73do1q6g
origin: https://steggate-core.onrender.com
repo: StegVerse-Labs/StegCore
branch: main
auto-deploy: yes
plan: free
region: oregon
```

Initial deploy:

```text
deploy id: dep-d9rlicajobas73do1qjg
status: build_failed
cause: workspace has run out of build pipeline minutes for the current billing period
```

Render's own build log states that builds are canceled until workspace build-pipeline capacity is restored. This is not a StegGate source/test failure and must not be represented as live activation.

## Claim and collision control

```text
task: STEGGATE-FULL-FUNCTIONAL-ACTIVATION-001
owner: StegVerse-Labs/StegCore#68
role: architecture reconciliation + implementation + validation + deployment activation
claim state: ACTIVE / HOST_DEPLOYMENT_BLOCKED
claim release condition: architecture reconciled, hosted /health + /v1/self-test + /v1/evaluate observed successfully
collision boundary: do not create a competing canonical StegGate service or parallel admissibility authority
```

Legacy Render services `steggate-api` and `steggate-api-tp4t` remain owned by `StegGhost/entity-sandbox-runner`; they are not evidence that canonical StegCore is deployed.

## Exact next executable actions

1. Finish the call graph from Governance artifacts through `three_layer.py`, permission/admissibility invariants, decision-state normalization, commit coherence, `governed_execute`, adapters, execution observation, and Continuity/reconciliation.
2. Classify every responsibility in provisional `steggate.py`/`service.py` as adapter, normalization, missing semantic, or duplicate/refactor target.
3. Refactor duplicate authority so the live API exposes one canonical admissibility chain.
4. Run repository tests and the session-context worker; retain exact workflow evidence.
5. When Render build-pipeline capacity becomes machine-observably available, allow the existing `steggate-core` service to deploy current `main`.
6. Inspect deploy to `live`, observe `/health`, require four-outcome `/v1/self-test`, and exercise `/v1/evaluate` with complete decision-state output.
7. Update issue #68, context worker state, and this handoff from direct evidence only.

## Cross-repository dependencies

Ara decision-state interop remains canonical at `StegVerse-Labs/ara-admissibility-interop/ARA_ADMISSIBILITY_INTEROP_MIRROR_HANDOFF.md`.
Continuity preservation remains canonical at `StegVerse-Labs/Continuity/STEGGATE_CONTINUITY_MIRROR_HANDOFF.md`.
Governance remains policy authority; StegCore remains runtime authority.

## Archive condition

NOT SATISFIED. The active goal is full functional StegGate activation, architecture reconciliation is still in progress, the live service remains provisional, and canonical hosted runtime observation is blocked by Render build-minute exhaustion. `data/steggate-session-context.json` explicitly sets `archive_allowed=false`; the worker must fail closed on context loss or premature archival state.
