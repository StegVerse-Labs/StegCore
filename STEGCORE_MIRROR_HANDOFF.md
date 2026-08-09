# StegCore Mirror Handoff

## Source of truth

```text
Organization: StegVerse-Labs
Repository: StegCore
Branch: main
Completed functional goal: STEGGATE-FULL-FUNCTIONAL-ACTIVATION-001 / issue #68 CLOSED
Completed integration goal: STEGGATE-HEARTBEAT-CREDENTIAL-INTEGRATION-001 / issue #75
Current integration goal: STEGGATE-TUNNEL-CONTINUITY-HARDENING
Canonical StegGate owner: StegVerse-Labs/StegCore
Canonical scheduler/signal owner: StegVerse-Labs/.github single heartbeat
Canonical runtime transport: heartbeat-owned zero-credential public tunnel
Persistent Render authority: NONE
Session-local implementation claim: RELEASED / MERGED_INTO_CANONICAL_WORKSTREAM
```

Live repository/workflow evidence supersedes chat summaries. Read this handoff together with `StegVerse-Labs/.github/docs/ORG_MIRROR_HANDOFF.md`, `StegVerse-Labs/.github/control/heartbeat-subsignals.json`, `StegVerse-Labs/.github/control/worker-registry.json`, `StegVerse-Labs/.github/handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json`, `StegVerse-Labs/.github/receipts/steggate-transport-lease/STEGGATE-TUNNEL-LEASE-001.json`, `.github/workflows/steggate-heartbeat-worker-reusable.yml`, `management/steggate-heartbeat-credential-integration.json`, and `data/steggate-live-activation-receipt.json`.

## Canonical authority chain

```text
Governance policy/evidence
  -> src/stegcore/three_layer.py:evaluate_three_layer
  -> src/stegcore/steggate.py:evaluate_admissibility
  -> ALLOW|DENY|REVIEW|FAIL_CLOSED
  -> src/stegcore/steggate_runtime.py:governed_steggate_execute
  -> src/stegcore/commit_governance.py:coherence_gate
  -> bounded consequence only after ALLOW + coherence ALLOW
  -> observation/reconciliation
```

Transport discovery, heartbeat cadence, and lease state do not grant StegGate execution or policy authority.

## Functional activation — COMPLETE

Issue #68 is closed. Canonical first activation remains merged through PR #74 / commit `1d26a21354917a74b40a6c8f1101d91e8d2c44c0`.

```text
data/steggate-live-activation-receipt.json
state: COMPLETE
deployment_source: heartbeat_ephemeral_micronode
observed_at: 2026-08-09T09:14:06.578269Z
```

The receipt is historical activation evidence. It is not rewritten on every heartbeat.

## Corrected heartbeat lease semantics — INSTALLED AND LIVE

The transport lease is **not per heartbeat**. Heartbeats are the signaling carrier; the lease is a subsignal-controlled continuity object.

Canonical current subsignal:

```text
StegVerse-Labs/.github/control/heartbeat-subsignals.json
subsignal: steggate_transport_lease
schema: stegverse.heartbeat-subsignals/v1
lease_id: STEGGATE-TUNNEL-LEASE-001
state: OPEN
lease_action: EXTEND
opened_epoch: 10
current heartbeat epoch observed: 17
```

The lease persists independently of heartbeat occurrence. A heartbeat may open, extend, hand off, or close the lease, but the heartbeat epoch itself is not the lease lifetime.

Release semantics:

```text
1. explicit CLOSE subsignal for the current lease; OR
2. accepted successor lease handoff; OR
3. all declared tunnel-dependent tasks reach terminal state.
```

Wall-clock expiry is not governance authority. A host/runtime envelope may force reconstruction, but that infrastructure limit does not redefine lease validity; the next admitted carrier reconstructs/extends the same governed lease state.

## Live lease proof

Canonical hosted validation run:

```text
StegVerse-Labs/.github workflow run: 31325697942
heartbeat job: 93275589574 SUCCESS
heartbeat epoch persisted: 10
micro-node job: 93275629397
Start zero-credential public transport: SUCCESS
Verify complete public acceptance: SUCCESS
Hold and self-heal tunnel under heartbeat lease subsignal: observed IN_PROGRESS after heartbeat job completion
```

This proved the corrected relationship directly: heartbeat epoch 10 completed while the StegGate micro-node remained active afterward under `STEGGATE-TUNNEL-LEASE-001`.

Durable org-level receipt:

```text
StegVerse-Labs/.github/receipts/steggate-transport-lease/STEGGATE-TUNNEL-LEASE-001.json
state: OPEN
runtime_state: LEASE_HOLD_SELF_HEAL_IN_PROGRESS
lease_is_per_heartbeat: false
wall_clock_expiry_authority: false
render_dependency: false
```

## Dependent-task participation

`StegVerse-Labs/.github/scripts/manage_heartbeat_subsignal.py` is the canonical mutation surface for dependent-task and lease lifecycle changes. It supports `register`, `unregister`, `open`, `extend`, `close`, and `handoff` and rejects invalid state/authority semantics. Commit: `26540ef445a90e80b5adfefcf211b735226e33ea`.

An empty dependent-task set does not automatically release an open lease. When dependent tasks are declared, the active micro-node consults the canonical worker registry and releases on task completion only when every declared task reaches a configured terminal state.

## Convergence and canonical continuation

The remaining carrier-successor/reconstruction requirement is not a separate chat-owned implementation lane. It converges with the organization-level sovereign restart/replacement continuity goal already activated through the canonical heartbeat worker registry.

```text
MERGED INTO: StegVerse-Labs/.github/handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json
worker registry: StegVerse-Labs/.github/control/worker-registry.json#SHWP-DURABLE-RUNTIME-ACTIVATION
worker: sovereign-runtime-activation-worker
claim: SHWP-SHWP-DURABLE-RUNTIME-ACTIVATION-G18
executor_binding: BOUND
worker_instance: sovereign-runtime-activation-worker-HB15-G18
lease clock: canonical heartbeat cycle
current worker transition: SOVEREIGN_NODE_RUNTIME_NOT_YET_OBSERVED
machine release condition: node-local activation.latest.json proves all sovereign runtime predicates
```

That worker's success predicates already require carrier restart/replacement, durable state reconstruction, heartbeat/registry continuity, and no claim/fence split brain. For an OPEN StegGate transport lease, the StegGate-specific acceptance evidence remains produced by the canonical heartbeat integration/reusable micro-node workflow; it is not delegated to Render or another scheduler.

Current continuation workflow observation at consolidation time:

```text
StegVerse-Labs/.github workflow: .github/workflows/steggate-heartbeat-integration.yml
latest observed run: 31333103959
state observed: PENDING
referenced StegCore reusable workflow commit: 61a829025baf41e0514d81e4169f966eaf1710dc
lease source: control/heartbeat-subsignals.json#steggate_transport_lease
```

The current run is machine-owned continuation. A fresh carrier is accepted only after `/health`, exact four-disposition `/v1/self-test`, and deterministic `/v1/evaluate` pass. A pending run is not counted as fresh acceptance.

## Implementation commits

```text
StegVerse-Labs/.github
  heartbeat subsignal schema                         00adef98237b692e65387cffc089cd0602bc8495
  heartbeat integration + safe rebase                2f13e7472377185250c4365460468111a95ea356
  lease opening receipt                              429fb3eac002b4176194abe48931b13964f638c6
  OPEN / EXTEND subsignal state                      7d073bf302c2c905cb366a59deffa57edb375b76
  dependent-task lifecycle manager                   26540ef445a90e80b5adfefcf211b735226e33ea

StegVerse-Labs/StegCore
  lease-bound self-healing reusable micro-node       229e8c99b77f8965fb3f07eea62d320d2d6d1ec6
```

## Third-party posture

Render is non-authoritative and not an activation dependency. The credentialed `stegverse.org/api/steggate` route remains optional stable-rendezvous hardening under Site; missing Cloudflare credential values do not block the heartbeat-tunnel lane.

## Session goal inventory and disposition

```text
1. Canonical StegGate functional activation: COMPLETE; issue #68 closed; activation receipt committed.
2. Remove Render as activation authority: COMPLETE; heartbeat zero-credential tunnel is canonical.
3. Verify tunnel /health, /v1/self-test, deterministic /v1/evaluate: COMPLETE for first activation and epoch-10 lease opening.
4. Correct lease semantics from per-heartbeat to heartbeat-subsig controlled continuity: COMPLETE and live.
5. Hold/self-heal carrier beyond heartbeat occurrence: COMPLETE and observed in run 31325697942.
6. Dependent-task lease participation: COMPLETE; canonical lifecycle manager installed.
7. Successor/reconstruction continuity proof: NOT YET TERMINAL; MERGED INTO canonical heartbeat/worker continuation plus canonical StegGate integration workflow.
8. Persistent stable rendezvous: OPTIONAL HARDENING; machine-owned separately by STEGGATE-STABLE-RENDEZVOUS-WORKER-001; not activation authority.
9. Render build-capacity monitoring: SUPERSEDED/OBSOLETE for StegGate activation.
```

No unique requirement remains only in chat history.

## Archive condition

The functional StegGate goal is activated. The remaining sovereign carrier/reconstruction production goal is durably owned by a documented StegVerse worker that is actually BOUND and cycle-leased through the canonical heartbeat and worker task registry. Therefore this session does not need to remain open to preserve execution authority.

Canonical continuation locations:

```text
StegVerse-Labs/.github/docs/ORG_MIRROR_HANDOFF.md
StegVerse-Labs/.github/control/heartbeat-subsignals.json
StegVerse-Labs/.github/control/worker-registry.json#SHWP-DURABLE-RUNTIME-ACTIVATION
StegVerse-Labs/.github/handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json
StegVerse-Labs/.github/.github/workflows/steggate-heartbeat-integration.yml
StegVerse-Labs/StegCore/.github/workflows/steggate-heartbeat-worker-reusable.yml
```

## Completeness

```text
functional StegGate: 100%
heartbeat transport activation: 100%
lease-subsig contract/install: 100%
first live lease opening/hold: 100%
dependent-task lifecycle control: 100%
successor/reconstruction production proof: machine-owned, pending
session-specific requirements transferred/completed: 9/9
scaffolding/stubs in completed StegGate runtime: 0
session unique active claims: 0
archive readiness under documented-heartbeat-worker alternative: YES
```
