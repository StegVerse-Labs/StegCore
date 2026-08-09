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
```

Live repository/workflow evidence supersedes chat summaries. Read this handoff together with `StegVerse-Labs/.github/docs/ORG_MIRROR_HANDOFF.md`, `StegVerse-Labs/.github/control/heartbeat-subsignals.json`, `StegVerse-Labs/.github/receipts/steggate-transport-lease/STEGGATE-TUNNEL-LEASE-001.json`, `.github/workflows/steggate-heartbeat-worker-reusable.yml`, `management/steggate-heartbeat-credential-integration.json`, and `data/steggate-live-activation-receipt.json`.

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

Canonical subsignal:

```text
StegVerse-Labs/.github/control/heartbeat-subsignals.json
subsignal: steggate_transport_lease
schema: stegverse.heartbeat-subsignals/v1
lease_id: STEGGATE-TUNNEL-LEASE-001
state: OPEN
lease_action: EXTEND
opened_epoch: 10
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
micro-node job: 93275629397 IN_PROGRESS
Start zero-credential public transport: SUCCESS
Verify complete public acceptance: SUCCESS
Hold and self-heal tunnel under heartbeat lease subsignal: IN_PROGRESS
```

This proves the corrected relationship directly: the heartbeat job completed and persisted epoch 10 while the StegGate micro-node remained active afterward under `STEGGATE-TUNNEL-LEASE-001`. The tunnel is therefore governed by the lease subsignal rather than by the heartbeat lifetime.

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

`StegVerse-Labs/.github/scripts/manage_heartbeat_subsignal.py` is the canonical mutation surface for dependent-task and lease lifecycle changes. It supports `register`, `unregister`, `open`, `extend`, `close`, and `handoff` and rejects invalid state/authority semantics. Current commit: `26540ef445a90e80b5adfefcf211b735226e33ea`.

An empty dependent-task set does not automatically release an open lease. When dependent tasks are declared, the active micro-node consults the canonical worker registry and releases on task completion only when every declared task reaches a configured terminal state.

## Implementation commits

```text
StegVerse-Labs/.github
  heartbeat subsignal schema                         00adef98237b692e65387cffc089cd0602bc8495
  heartbeat integration + safe rebase                2f13e7472377185250c4365460468111a95ea356
  lease opening receipt                              429fb3eac002b4176194abe48931b13964f638c6
  OPEN / EXTEND subsignal state                      7d073bf302c2c905cb366a59deffa57edb375b76
  dependent-task lifecycle manager                   26540ef445a90e80b5adfefcf211b735226e33ea
  organization handoff reconciliation                1d2eadc53d7915e6ddea0be62a451261c6c91329

StegVerse-Labs/StegCore
  lease-bound self-healing reusable micro-node       229e8c99b77f8965fb3f07eea62d320d2d6d1ec6
```

## Third-party posture

Render is non-authoritative and not an activation dependency. The credentialed `stegverse.org/api/steggate` route remains optional stable-rendezvous hardening under Site; missing Cloudflare credential values do not block the heartbeat-tunnel lane.

## Remaining work

```text
StegVerse-Labs/.github:
  - make successor-lease acceptance/handoff machine-observable across carriers
  - preserve an explicit reconstruction signal when a carrier host envelope ends before lease release
  - validate at least one successor/reconstruction opening under the same governing lease semantics

StegVerse-Labs/StegCore:
  - preserve final lease runtime evidence when the current carrier releases/reconstructs
  - keep endpoint discovery fail-closed against stale origins
```

No scaffolding-only transport implementation is counted as activation and no manual user action is assigned.

## Completeness

```text
functional StegGate: 100%
heartbeat transport activation: 100%
lease-subsig contract/install: 100%
first live lease opening/hold: 100%
dependent-task lifecycle control: 100% installed
successor/reconstruction proof: pending
scaffolding/stubs in completed StegGate runtime: 0
archive readiness for this lease-continuity goal: NO
```
