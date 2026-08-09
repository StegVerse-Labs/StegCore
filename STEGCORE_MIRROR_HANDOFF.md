# StegCore Mirror Handoff

## Source of truth

```text
Organization: StegVerse-Labs
Repository: StegCore
Canonical branch: main
Primary goal: STEGGATE-FULL-FUNCTIONAL-ACTIVATION-001
Canonical task owner: issue #68 + repository-native workers + active originating session
Project state: ARCHITECTURE_RECONCILED / RESIDENT RUNTIME VALIDATED / PORTABLE EPHEMERAL TOPOLOGY ACTIVE / PUBLIC FALLBACK PROVEN / STABLE RESIDENT ENDPOINT STILL UNRESOLVED
Originating chat state: ACTIVE_UNIQUE_WORK_REMAINS / DO NOT ARCHIVE UNTIL FULL GOAL ACTIVATED
```

Read this file before changing StegCore runtime decisions, adapters, package topology, live-service activation, deployment, or downstream verification. Live Git state, workflow runs/jobs, committed evidence, issue #68, `data/steggate-session-context.json`, `data/steggate-architecture-reconciliation-state.json`, `management/steggate-full-functional-activation.json`, and `management/steggate-portable-micronode-activation.json` supersede chat summaries.

## Active goal

Make canonical StegGate actually functional through one authoritative admissibility-to-consequence chain across the deployment topologies that use it. Persistent HTTP hosting is one topology, not the definition of StegGate. A portable governed package may instantiate an ephemeral StegGate micro-node locally at the consequence boundary.

Do not create a parallel decision authority because `decision.py` is intentionally minimal. Do not reproduce StegGate policy logic in Site, a consumer, a tunnel, or a rendezvous layer. Do not archive the originating session while the broader full-functional activation goal still has unique integration work.

## Canonical authority chain — RECONCILED

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
injected consequence callback at governed commit boundary
        ↓
execution observation / runtime_adapters reconciliation semantics
        ↓
Continuity/reconstruction consumers
```

Architectural facts:

1. `src/stegcore/decision.py` remains a deliberately minimal compatibility interface, not the canonical full engine.
2. `src/stegcore/three_layer.py` is the core evaluator for judgment, signal/reference-state integrity, and execution-boundary authority/policy/delegation/evidence/recoverability.
3. `src/stegcore/steggate.py` composes that evaluator into the complete decision-state matrix and candidate-bound REVIEW semantics; it is not a second policy engine.
4. `src/stegcore/steggate_runtime.py` binds full decision state to independent commit coherence before any injected consequence callback is reachable.
5. DENY, REVIEW, FAIL_CLOSED, coherence denial, or missing commit authority cannot invoke the consequence callback.
6. Complete decision state, including non-occurrence and divergence, remains reconstructable reality.

## Functional topologies

### A. Resident HTTP StegGate

Implemented surfaces:

```text
src/stegcore/service.py
scripts/observe_steggate_live_service.py
scripts/finalize_steggate_live_activation.py
src/stegcore/endpoint_discovery.py
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

The resident HTTP service exposes evaluation only. It does not expose an arbitrary remote mutation callback or gain deployment, Continuity, publication, legal, custody, payment, or external-system authority.

The original Render service still exists:

```text
name: steggate-core
service_id: srv-d9rlic2jobas73do1q6g
origin: https://steggate-core.onrender.com
repo: StegVerse-Labs/StegCore
branch: main
auto_deploy: yes
```

Render remains blocked before source build execution by exhausted workspace build-pipeline minutes. Paid workspace changes are not authorized by this goal.

A zero-spend GitHub Actions + Cloudflare Quick Tunnel fallback proved that the canonical HTTP service can run publicly and pass `/health`, exact four-disposition `/v1/self-test`, and complete-matrix `/v1/evaluate`. Quick Tunnel endpoints are ephemeral and were not reliably reachable from an independent subsequent runner, so they are proof/transport nodes rather than a stable service identity.

`src/stegcore/endpoint_discovery.py` therefore verifies endpoint health independently and fails closed on a stale/unreachable registry declaration.

### B. Portable / ephemeral governed-package StegGate — ACTIVE

Canonical record: `management/steggate-portable-micronode-activation.json`.
Design: `docs/STEGGATE_PORTABLE_MICRONODE.md`.
Implementation: `src/stegcore/portable_steggate.py`.
Tests: `tests/test_portable_steggate.py`.

Principle:

> A governed transition and the StegGate boundary required to admit it may travel as one transportable execution object.

A `GovernedTransitionPackage` carries the canonical `AdmissibilityRequest`, package identity/hash, portable-node profile, expected reconciled-runtime profile/fingerprint, declared execution/coherence context, and optional expiry. It does not gain trust by transporting arbitrary executable bytes.

The receiver instantiates a fresh short-lived `SGMU-*` micro-node from a locally installed known StegCore runtime, verifies package and runtime binding, runs the canonical authority chain, emits a `stegcore.portable_micronode_receipt`, and terminates.

Lifecycle:

```text
TRANSPORTED
  → INSTANTIATED
  → PACKAGE_AND_RUNTIME_BINDING_VERIFIED
  → EVALUATED
  → [COMMIT_COHERENCE if execution requested]
  → [CONSEQUENCE only if ALLOW + coherence ALLOW]
  → RECEIPT_EMITTED
  → TERMINATED
```

Fail-closed before consequence on:

- package hash mismatch;
- runtime fingerprint mismatch;
- invalid or expired package validity;
- canonical non-ALLOW admissibility;
- independent coherence denial.

Networking is optional. A portable node can execute locally beside the governed consequence adapter and therefore does not require Render, a public ingress, a stable URL, or a tunnel.

Hosted validation for this topology:

```text
StegCore Tests run: 31286273932
job: 93175594894
head: 2f0076a25fdf7ee020dca85f3934c6bca385b310
result: PASS
161 tests passed
129 subtests passed
artifact: 9029913625
artifact sha256: fd7b9a27eb18d6e4a061e7e7b507cceb6d6b10bef649e2198c08841a9e25e054
```

The tests prove JSON transport + fresh instantiation, canonical execution after ALLOW+coherence ALLOW, runtime-fingerprint fail-closed behavior, package-tamper fail-closed behavior, and no executor invocation on canonical DENY.

**Portable topology activation state: COMPLETE_AND_HOSTED_VALIDATED.**

## Worker/context retention — ACTIVE

Canonical worker surfaces:

```text
data/steggate-session-context.json
scripts/guard_steggate_session_continuity.py
tests/test_steggate_session_continuity.py
.github/workflows/steggate-session-continuity.yml
```

The worker preserves the active full-functional goal, prevents intentional minimal interfaces from being misclassified as missing engines, prevents duplicate canonical decision authority, and fails closed if an incomplete goal is prematurely marked archive-ready.

Hosted green evidence remains run `31276136526`, job `93149840636`, artifact `9027042689`, digest `sha256:212d757d9c155baeb6303c6b7a28fc3d31c0a95fb36d4203b8343df29b4883af`.

## Current claim and collision control

```text
task_id: STEGGATE-FULL-FUNCTIONAL-ACTIVATION-001
repository: StegVerse-Labs/StegCore
branch: main
canonical owner: issue #68 + repository-native automation + active originating session
chat claimant: ACTIVE_UNIQUE_WORK_REMAINS
collision boundary: no competing StegGate policy engine; no consumer may reinterpret package transport as policy authority
claim release condition: full functional goal has no remaining unique integration/activation work and all required consumer/runtime observations are durable
```

Completed subgoals:

- `FF-CONTEXT-01` context-retention worker: COMPLETE.
- `FF-ARCH-02` canonical architecture reconciliation: COMPLETE.
- `FF-EXEC-03` evaluation → coherence → consequence composition: COMPLETE.
- `FF-SERVICE-04` resident HTTP evaluation service implementation: COMPLETE.
- `FF-PORTABLE-08` portable ephemeral governed-package micro-node: COMPLETE_AND_HOSTED_VALIDATED.
- Public HTTP execution through an ephemeral Cloudflare transport: PROVEN, but not accepted as stable endpoint continuity.

Open work:

1. `FF-CONSUMER-09` — bind at least one real StegVerse consumer/provider adapter to `GovernedTransitionPackage` and execute/evaluate locally without public StegGate ingress. Candidate consumers: Ecosystem Chat, VACC, Math Solver, HIL. This is now the highest-value unblocked functional proof.
2. `FF-RESIDENT-STABLE-10` — if a resident remote StegGate endpoint remains required by a consumer, converge it with StegVerse-owned endpoint publication/discovery rather than treating Render as architectural authority. Site issue #24 already owns the general endpoint-publication/fail-closed routing architecture; do not duplicate its authority.
3. Existing Render and live-observer automation remain valid as a resident-topology lane, but failure of that lane does not invalidate the portable topology.

## Cross-repository boundaries

- Governance remains policy/evidence authority.
- `StegVerse-Labs/ara-admissibility-interop` remains interop/schema owner for decision-state portability.
- `StegVerse-Labs/Continuity` remains Continuity/reconstruction consumer authority.
- Site issue #24 owns the StegVerse-owned endpoint-publication/discovery architecture for stable routing where remote ingress is needed.
- Consumers may construct/transport governed packages and provide bounded consequence adapters; they must not duplicate StegGate policy evaluation.

## Next executable action

Select the first nonconflicting consumer whose canonical handoff permits integration, read its handoff, and install a thin adapter that:

1. constructs or accepts `GovernedTransitionPackage`;
2. transports the package without rewriting its governance semantics;
3. instantiates `evaluate_governed_package` or `execute_governed_package` locally;
4. supplies only the consumer-specific bounded consequence callback;
5. preserves the returned portable micro-node receipt for reconstruction;
6. proves no public StegGate ingress is required.

## Archive condition

NOT SATISFIED.

Portable micro-node activation is complete, but the broader full-functional goal still has a unique integration proof remaining: a real consumer must use the portable package topology without duplicating decision authority. The originating session remains active until that integration is installed/validated or durably transferred to an already-claimed canonical consumer lane with no unique chat-only requirements remaining.
