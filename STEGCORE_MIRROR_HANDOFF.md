# StegCore Mirror Handoff

## Source of truth

```text
Organization: StegVerse-Labs
Repository: StegCore
Branch: main
Completed functional goal: STEGGATE-FULL-FUNCTIONAL-ACTIVATION-001 / issue #68 CLOSED
Completed integration goal: STEGGATE-HEARTBEAT-CREDENTIAL-INTEGRATION-001 / issue #75
Current integration direction: STEGGATE-TUNNEL-CONTINUITY-HARDENING
Canonical StegGate owner: StegVerse-Labs/StegCore
Canonical scheduler: StegVerse-Labs/.github single heartbeat
Canonical runtime transport lane: heartbeat-owned ephemeral micro-node + zero-credential public tunnel
Persistent Render authority: NONE
Credentialed named route requirement: OPTIONAL HARDENING ONLY
```

Live repository/workflow evidence supersedes older chat summaries. Read this handoff, `management/steggate-heartbeat-credential-integration.json`, `data/steggate-live-activation-receipt.json`, `management/steggate-full-functional-activation.json`, `.github/workflows/steggate-heartbeat-worker-reusable.yml`, `.github/workflows/steggate-fallback-public-runtime.yml`, and the canonical heartbeat records in `StegVerse-Labs/.github` before changing this workstream.

## Canonical StegGate authority chain

```text
Governance policy/evidence
  -> src/stegcore/three_layer.py:evaluate_three_layer
  -> src/stegcore/steggate.py:evaluate_admissibility
  -> complete admissibility matrix / ALLOW|DENY|REVIEW|FAIL_CLOSED
  -> src/stegcore/steggate_runtime.py:governed_steggate_execute
  -> src/stegcore/commit_governance.py:coherence_gate
  -> bounded consequence callback only after ALLOW + coherence ALLOW
  -> execution observation/reconciliation
  -> Continuity/reconstruction consumers
```

`decision.py` remains an intentionally minimal compatibility interface. Do not create a competing evaluator.

## Functional activation — COMPLETE

Issue #68 is closed. Canonical activation remains persisted through merged PR #74 / merge commit `1d26a21354917a74b40a6c8f1101d91e8d2c44c0`.

Canonical first-activation receipt:

```text
data/steggate-live-activation-receipt.json
state: COMPLETE
deployment_source: heartbeat_ephemeral_micronode
observed_at: 2026-08-09T09:14:06.578269Z
observation_digest: sha256:4159d510a8c8e2d941f8c5efb8355f95ce651c328b41e22abb8be7e97b799506
receipt_digest: sha256:8fa34d07283a48e5aacf71f8f11242371de5e997b61f16b055e403c10a07df13
```

That receipt is historical activation evidence and is not rewritten for every heartbeat. Current runtime continuity is established by heartbeat-bound workflow evidence and artifacts.

## Heartbeat-owned zero-credential tunnel — CURRENT CANONICAL RUNTIME LANE

The canonical organization heartbeat directly invokes StegCore's reusable micro-node workflow. The worker starts canonical StegGate locally, opens a zero-credential public tunnel, verifies `/health`, exact four-disposition `/v1/self-test`, and deterministic complete-matrix `/v1/evaluate`, then preserves heartbeat/tunnel evidence.

Fresh proof:

```text
StegVerse-Labs/.github workflow run: 31325104576
heartbeat job: 93274099310 SUCCESS
micro-node job: 93274112655 SUCCESS
heartbeat id: HB-31325104576-5
heartbeat epoch: 5
StegCore commit executed: f0d764b2b5b48987d75ea4efd1da1fafde04b406
observed tunnel origin: https://owners-recipes-catherine-laid.trycloudflare.com
health: PASS
self-test: PASS
v1/evaluate: PASS
heartbeat artifact: 9041292966
heartbeat artifact digest: sha256:bc0c6d498f0f270f2fa1ec2de29444b4d2cd809d726287fb70f36f2decb9e919
micro-node artifact: 9041297862
micro-node artifact digest: sha256:a1222757e3fe0187b58ce2bd26c32600c70087c14c5f9e48f68ee7ffa2473b69
```

The deterministic evaluation returned `ALLOW`, canonical three-layer `ALLOW`, all required matrix predicates PASS, permission/admissibility separation true, no external execution, and no continuity receipt minted by observation.

The previous issue-comment registry entry from 09:14 UTC is historical rotating-endpoint evidence, not proof that the same tunnel remains live indefinitely. Consumers must independently health-check any registry origin.

## Portable topology — COMPLETE

`src/stegcore/portable_steggate.py` remains the first-class governed-package topology. Networking is optional; a receiver can instantiate a bounded local micro-node, evaluate the canonical chain, emit reconstructable evidence, and terminate.

## Scheduling model

`.github#12` owns the single StegVerse heartbeat. Heartbeat cadence and epoch do not grant execution authority. The canonical `.github -> StegCore` carrier is the reusable workflow call with the exact heartbeat ID and epoch. StegCore may still accept `repository_dispatch: stegverse-heartbeat` for compatible carriers, but no wall-clock scheduler is normative.

Authoritative surfaces:

```text
StegVerse-Labs/.github/.github/workflows/steggate-heartbeat-integration.yml
StegVerse-Labs/.github/management/STEGGATE_HEARTBEAT_CREDENTIAL_INTEGRATION_001.json
StegVerse-Labs/StegCore/.github/workflows/steggate-heartbeat-worker-reusable.yml
StegVerse-Labs/StegCore/.github/workflows/steggate-fallback-public-runtime.yml
StegVerse-Labs/StegCore/management/steggate-heartbeat-credential-integration.json
```

## Third-party hosting and stable-route posture

Render is non-authoritative and not an activation dependency. Build capacity on Render must not block StegGate execution, verification, or continuity.

The credentialed `stegverse.org/api/steggate` route owned by `StegVerse-Labs/Site#24` is optional stable-rendezvous hardening only. Its current missing Cloudflare credential values are not a functional blocker. TV/TVC retain their no-secret credential-reference and read-authority contracts for that optional lane, but they do not manufacture secret values and are not required for heartbeat-tunnel activation.

## Collision controls

- `.github#12` owns the single StegVerse heartbeat.
- StegCore owns StegGate evaluation/runtime.
- Transport discovery never grants StegGate authority.
- Site must not copy StegGate policy logic.
- Render and Cloudflare availability do not define StegGate admissibility.
- The rotating tunnel endpoint is evidence-bound and must be health-verified before use.
- `StegVerse-org/LLM-adapter` remains the real Ecosystem Chat consumer/custody lane; do not duplicate it here.

## Current execution inventory

Authoritative inventory: `management/steggate-heartbeat-credential-integration.json`.

```text
HBI-01 heartbeat-native StegCore trigger surface                       COMPLETE
HBI-02 fresh heartbeat -> zero-credential tunneled micro-node proof    COMPLETE
HBI-03 TV credential-reference packaging                              COMPLETE
HBI-04 TVC exact-bound no-secret authority for optional stable lane    COMPLETE
HBI-05 Site credentialed named route                                  OPTIONAL HARDENING / NOT ACTIVATION DEPENDENCY
HBI-06 handoff/inventory/runtime-authority reconciliation              COMPLETE
```

## Next integration goal

`STEGGATE-TUNNEL-CONTINUITY-HARDENING`

Goal: keep the heartbeat-owned tunnel/runtime evidence current and make endpoint discovery consume only a presently verified heartbeat-owned origin, while continuing to fail closed when no current endpoint exists. Do not introduce a persistent hosting dependency to satisfy this goal.

## Completeness

```text
functional StegGate goal: 100%
heartbeat/transport integration goal: 100%
developed current-goal files: 13/13
scaffolding/stubs: 0
validation groups: 6/6
integration groups: 6/6
next goal activation: started by epoch-5 tunnel proof
archive readiness: NO — downstream Site handoff still needs the same optional-stable-route reconciliation
```
