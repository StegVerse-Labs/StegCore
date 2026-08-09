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

Live repository/workflow evidence supersedes chat summaries. Read this handoff together with `StegVerse-Labs/.github/docs/ORG_MIRROR_HANDOFF.md`, `StegVerse-Labs/.github/control/heartbeat-subsignals.json`, `.github/workflows/steggate-heartbeat-worker-reusable.yml`, `management/steggate-heartbeat-credential-integration.json`, and `data/steggate-live-activation-receipt.json`.

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

## Fresh zero-credential tunnel proof

Fresh accepted proof remains:

```text
StegVerse-Labs/.github run: 31325104576
heartbeat job: 93274099310 SUCCESS
micro-node job: 93274112655 SUCCESS
heartbeat: HB-31325104576-5 / epoch 5
health: PASS
self-test exact four dispositions: PASS
v1/evaluate deterministic complete matrix: PASS
micro-node artifact: 9041297862
artifact digest: sha256:a1222757e3fe0187b58ce2bd26c32600c70087c14c5f9e48f68ee7ffa2473b69
```

Historical rotating endpoint declarations never prove indefinite liveness; consumers health-check the current origin.

## Corrected heartbeat lease semantics

The transport lease is **not per heartbeat**. Heartbeats are the signaling carrier; the lease is a subsignal-controlled continuity object.

Canonical subsignal:

```text
StegVerse-Labs/.github/control/heartbeat-subsignals.json
subsignal: steggate_transport_lease
schema: stegverse.heartbeat-subsignals/v1
lease actions: NONE | OPEN | EXTEND | CLOSE
```

The lease persists independently of heartbeat occurrence. A heartbeat may open, extend, hand off, or close the lease, but the heartbeat epoch itself is not the lease lifetime.

Release semantics:

```text
1. explicit CLOSE subsignal for the current lease; OR
2. accepted successor lease handoff; OR
3. all declared tunnel-dependent tasks reach terminal state.
```

Wall-clock expiry is not governance authority. A host/runtime envelope may force reconstruction, but that infrastructure limit does not redefine lease validity; the next admitted carrier reconstructs/extends the same governed lease state.

Current implementation commits:

```text
StegVerse-Labs/.github
  schemas/heartbeat-subsignal.schema.json        00adef98237b692e65387cffc089cd0602bc8495
  control/heartbeat-subsignals.json              09100d98efe0b043c4382c98727180cf79f76fc0
  steggate-heartbeat-integration.yml             2f13e7472377185250c4365460468111a95ea356

StegVerse-Labs/StegCore
  steggate-heartbeat-worker-reusable.yml         229e8c99b77f8965fb3f07eea62d320d2d6d1ec6
```

The reusable worker now receives lease identity/action/dependent-task state, binds it into runtime evidence, maintains and self-heals the tunnel while the lease remains admitted, and releases only under the subsignal/task conditions above.

## Validation state

The first lease-bearing integration run `31325629644` was a startup failure because it resolved the older reusable workflow SHA before the new inputs existed. The next run `31325667609` resolved the corrected reusable SHA but exposed an existing heartbeat persistence defect: runtime-generated unstaged files prevented `git pull --rebase`.

That persistence path has now been corrected in `.github` commit `2f13e7472377185250c4365460468111a95ea356` by stashing noncanonical runtime evidence across the canonical rebase/push and restoring it for artifact preservation.

Current validation run: `31325697942`; it resolves StegCore reusable commit `229e8c99b77f8965fb3f07eea62d320d2d6d1ec6`. At last observation its heartbeat job was queued. Do not claim live lease activation until that run reaches tunneled acceptance.

## Third-party posture

Render is non-authoritative and not an activation dependency. The credentialed `stegverse.org/api/steggate` route remains optional stable-rendezvous hardening under Site; missing Cloudflare credential values do not block the heartbeat-tunnel lane.

## Remaining work

```text
StegVerse-Labs/.github:
  - complete hosted validation of run 31325697942 or successor
  - persist/advance lease subsignal state from OPEN_REQUESTED to observed OPEN after public acceptance
  - add successor-lease acceptance writeback so handoff is machine-observable
  - allow tunnel-dependent workers/tasks to register/deregister their lease dependency

StegVerse-Labs/StegCore:
  - validate lease-hold/self-heal loop in hosted execution
  - preserve final lease runtime evidence artifact
  - keep endpoint discovery fail-closed against stale origins
```

No scaffolding-only transport implementation is counted as activation.

## Completeness

```text
functional StegGate: 100%
heartbeat transport activation: 100%
lease-subsig contract/install: 90%
hosted lease validation: pending
scaffolding/stubs in completed StegGate runtime: 0
archive readiness for this lease-correction work: NO
```
