# StegCore Mirror Handoff

## Source of truth

```text
Organization: StegVerse-Labs
Repository: StegCore
Branch: main
Completed functional goal: STEGGATE-FULL-FUNCTIONAL-ACTIVATION-001 / issue #68 CLOSED
Completed integration goal: STEGGATE-HEARTBEAT-CREDENTIAL-INTEGRATION-001 / issue #75
Current continuity goal: STEGGATE-TUNNEL-CONTINUITY-HARDENING
Current product integration goal: STEGGATE-FOUR-APP-RUNTIME-BINDING-001 / issue #70
Canonical StegGate owner: StegVerse-Labs/StegCore
Canonical scheduler/signal owner: StegVerse-Labs/.github single heartbeat
Canonical runtime transport: heartbeat-owned zero-credential public tunnel
Persistent Render authority: NONE
Active #70 implementation claim: current-session-common-runtime-binding / CLAIMED_FOR_IMPLEMENTATION
```

Live repository/workflow evidence supersedes chat summaries. Read this handoff together with `StegVerse-Labs/.github/docs/ORG_MIRROR_HANDOFF.md`, `StegVerse-Labs/.github/control/heartbeat-subsignals.json`, `StegVerse-Labs/.github/control/worker-registry.json`, `StegVerse-Labs/.github/handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json`, `StegVerse-Labs/.github/receipts/steggate-transport-lease/STEGGATE-TUNNEL-LEASE-001.json`, `.github/workflows/steggate-heartbeat-worker-reusable.yml`, `management/steggate-heartbeat-credential-integration.json`, `management/steggate-four-app-runtime-binding.json`, `docs/STEGGATE_RUNTIME_IDENTITY_CONTRACT.md`, and `data/steggate-live-activation-receipt.json`.

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
  runtime identity endpoint + contract fields        fec0248d51083cf840ad983a5b0af83d4fc6db37
  runtime identity tests                             74273127c22f70995329774593236f299b98c854
  runtime identity contract documentation            8c484e584d60a3bd2763d6948d0eb3f4afd67e0c
  #70 durable claim/state                            267fde596f0857ed8bbe49b02155c0e9a164b7fe
```

## Four-app canonical runtime identity integration — ACTIVE

Issue #70 became executable when #68 closed. The canonical transport-independent binding contract is now implemented rather than inferred from an ephemeral tunnel URL.

```text
GET /v1/runtime-identity
contract_version: stegverse.steggate.runtime-identity.v1
runtime_identity: stegverse:steggate:canonical:three-layer:v1
canonical_owner: StegVerse-Labs/StegCore
canonical_admissibility_runtime: stegcore.three_layer.evaluate_three_layer
transport_identity_authoritative: false
```

The same identity is exposed through `/health`, `/v1/capabilities`, and `/v1/self-test`. This allows applications to bind to canonical StegGate semantics across heartbeat carrier replacement without making a host URL into policy authority.

Direct validation:

```text
StegCore Tests run: 31338809707
job: 93308982069 SUCCESS
artifact: 9045154237
artifact digest: sha256:e59d08fc0de1a4c4fdf893c5db1d857e20fe7e3fa77dc3cde44c1e6f4b2f6ab2
```

Current claim and remaining integration are in `management/steggate-four-app-runtime-binding.json`. The core contract is implemented and validated, but issue #70 MUST remain open until Ecosystem Chat, VACC, Math Solver, and HIL each retain direct evidence that their governed path consumed this canonical identity and traversed the canonical StegGate semantics. Static contract existence is not four-app integration completion.

Collision boundaries:

- do not modify HIL upload paths currently owned by the separate Site claimant;
- do not create per-application StegGate evaluators;
- do not bind canonical identity to an ephemeral or vendor-specific transport URL.

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
10. Four-app stable canonical runtime identity contract: IMPLEMENTED + CI VALIDATED; issue #70 application bindings remain ACTIVE.
```

## Archive condition

The StegCore functional activation goal is complete, but the parent session goal is `StegVerse-Labs/Site#239`: four public applications at directly verified functional production state. That parent is not complete. While this session owns the active #70 common-runtime-binding claim, it is not archiveable.

Canonical continuation locations:

```text
StegVerse-Labs/Site#239
StegVerse-Labs/StegCore#70
StegVerse-Labs/StegCore/management/steggate-four-app-runtime-binding.json
StegVerse-Labs/StegCore/docs/STEGGATE_RUNTIME_IDENTITY_CONTRACT.md
StegVerse-Labs/Site/docs/STEGGATE_FOUR_APP_MIRROR_HANDOFF.md
StegVerse-Labs/.github/control/heartbeat-subsignals.json
StegVerse-Labs/.github/control/worker-registry.json#SHWP-DURABLE-RUNTIME-ACTIVATION
```

## Completeness

```text
functional StegGate: 100%
heartbeat transport activation: 100%
stable runtime identity core contract: 100% implemented + CI validated
four-app direct identity bindings: 0/4 complete at this checkpoint
parent four-app direct runtime gates: follow Site machine status
scaffolding/stubs in completed StegGate runtime identity contract: 0
active session claim: #70 common-runtime-binding integration
archive readiness for parent session goal: NO
```
