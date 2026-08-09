# StegCore Mirror Handoff

## Source of truth

```text
Organization: StegVerse-Labs
Repository: StegCore
Branch: main
Active goal ID: STEGGATE-FULL-FUNCTIONAL-ACTIVATION-001
Originating session goal: make StegGate actually functional, preserving the complete admissibility matrix and decision/execution/observation state as reconstructable reality
Canonical owner: StegVerse-Labs/StegCore#68 + repository-native workers + active originating session
Implementation claim: ACTIVE — resident/stable endpoint acceptance remains
Validation claim: ACTIVE — portable topology and consumer are green; resident stable path remains
Claim release condition: issue #68 acceptance is satisfied or authoritatively superseded with equivalent evidence, all remaining integration evidence is durable, and no unique session role remains
Project state: PORTABLE_STEGGATE_ACTIVE / REAL_CONSUMER_INTEGRATED / RESIDENT_HTTP_IMPLEMENTED / PUBLIC_EPHEMERAL_HTTP_PROVEN / STABLE_RENDEZVOUS_BLOCKED_ON_DEPLOYMENT_CREDENTIALS
Session state: ACTIVE_UNIQUE_WORK_REMAINS
Archive allowed: NO
```

Read this handoff, `management/steggate-full-functional-activation.json`, `management/steggate-portable-micronode-activation.json`, `data/steggate-session-context.json`, `data/steggate-architecture-reconciliation-state.json`, and issue #68 before changing StegGate. Live Git/workflow evidence supersedes prior chat claims.

## Canonical authority chain

```text
Governance policy/evidence
  -> src/stegcore/three_layer.py:evaluate_three_layer
  -> src/stegcore/steggate.py:evaluate_admissibility
  -> complete admissibility matrix / ALLOW|DENY|REVIEW|FAIL_CLOSED
  -> src/stegcore/steggate_runtime.py:governed_steggate_execute
  -> src/stegcore/commit_governance.py:coherence_gate
  -> bounded consequence callback only after ALLOW + coherence ALLOW
  -> execution observation / reconciliation
  -> Continuity/reconstruction consumers
```

`decision.py` is an intentionally minimal compatibility interface, not the full engine. Do not infer missing functionality from that interface and do not build a competing evaluator.

## Completed work

### Core runtime and decision-state reconstruction

Complete and validated: canonical three-layer evaluation, full matrix normalization, candidate-bound REVIEW, fail-closed semantics, commit coherence, consequence inaccessibility on non-ALLOW, execution observation, divergence/bypass semantics, and complete decision-state preservation.

### Resident HTTP surface

Implemented:

```text
src/stegcore/service.py
src/stegcore/endpoint_discovery.py
scripts/observe_steggate_live_service.py
scripts/finalize_steggate_live_activation.py
.github/workflows/steggate-live-observer.yml
.github/workflows/steggate-fallback-public-runtime.yml
```

The public fallback workflow has successfully run canonical StegGate over a Cloudflare Quick Tunnel and passed `/health`, exact ALLOW/DENY/REVIEW/FAIL_CLOSED `/v1/self-test`, and complete-matrix `/v1/evaluate`. A Quick Tunnel is treated as an ephemeral transport node, not stable identity. Endpoint discovery independently verifies canonical health and fails closed on stale registry state.

Render `srv-d9rlic2jobas73do1q6g` remains a non-authoritative resident hosting lane and is blocked before source build by exhausted build-pipeline minutes.

### Portable / ephemeral governed-package topology — COMPLETE

Authoritative surfaces:

```text
src/stegcore/portable_steggate.py
tests/test_portable_steggate.py
docs/STEGGATE_PORTABLE_MICRONODE.md
management/steggate-portable-micronode-activation.json
```

A `GovernedTransitionPackage` carries the canonical `AdmissibilityRequest`, package identity/hash, portable-node profile, expected reconciled-runtime profile/fingerprint, execution/coherence context, and optional expiry. It does not acquire authority by transporting arbitrary executable bytes.

The receiver instantiates a fresh `SGMU-*` micro-node from a locally installed known StegCore runtime; verifies package hash, runtime fingerprint and validity; evaluates the canonical chain; optionally crosses commit coherence; invokes the bounded consequence only after ALLOW + coherence ALLOW; emits a reconstructable receipt; and terminates.

Networking is optional. Render, a public URL, or a tunnel is not required for this topology.

Hosted evidence:

```text
StegCore Tests run 31286273932
job 93175594894
head 2f0076a25fdf7ee020dca85f3934c6bca385b310
161 tests passed; 129 subtests passed
artifact 9029913625
sha256 fd7b9a27eb18d6e4a061e7e7b507cceb6d6b10bef649e2198c08841a9e25e054
```

### Real consumer integration — COMPLETE

Canonical consumer: `StegVerse-org/LLM-adapter` / Ecosystem Chat user-LLM path.

Consumer surfaces:

```text
llm_adapter/steggate_portable_consumer.py
tests/test_steggate_portable_consumer.py
.github/workflows/steggate-portable-consumer.yml
receipts/steggate-portable-consumer-integration.latest.json
LLM_ADAPTER_MIRROR_HANDOFF.md
```

Hosted evidence:

```text
LLM-adapter run 31286444819
job 93176065654
result SUCCESS
artifact 9029971776
sha256 c555e9035d480120d36184308d165e8e0987a0765c3020a60abf0c45f425c4f4
```

The consumer maps explicit governance facts into the canonical StegCore request, transports the governed package, and supplies only the bounded provider callback. Policy drift prevents the callback. No provider credential travels in the package. No public StegGate ingress is required. Decision authority is not duplicated.

## Stable micro-node rendezvous integration — IMPLEMENTED / DEPLOYMENT BLOCKED

The remaining resident/stable routing problem was converted from “make Quick Tunnel permanent” to “stable StegVerse rendezvous over rotating verified nodes.” This follows Site issue #24's existing endpoint-publication/fail-closed routing authority.

Installed in `StegVerse-Labs/Site`:

```text
src/steggate-rendezvous-worker.js
wrangler.steggate.jsonc
.github/workflows/steggate-rendezvous-deploy.yml
```

Stable intended route:

```text
https://stegverse.org/api/steggate/*
```

The Worker contains no StegGate policy logic. It reads the canonical micro-node registry, independently verifies selected-node `/health`, proxies only the bounded StegGate evaluation routes, and returns FAIL_CLOSED when no verified node is reachable.

Deployment run `31286621905` was attempted. It failed at `Validate deployment credentials` before Wrangler execution because the Site Actions runtime does not currently expose `CLOUDFLARE_API_TOKEN` and/or `CLOUDFLARE_ACCOUNT_ID`. No deployment success is claimed. Existing Site HIL Cloudflare deployment runs show the same credentials-dependent control plane.

Machine-observable release condition: authorized Site Cloudflare deployment credentials become available to Actions, or an already-authorized endpoint-publication plane deploys the same non-authorizing rendezvous contract.

## Collision control and cross-repository ownership

- Governance: policy/evidence authority.
- `StegVerse-Labs/ara-admissibility-interop`: decision-state interop/schema authority.
- `StegVerse-Labs/Continuity`: reconstruction/Continuity consumer authority.
- `StegVerse-org/LLM-adapter#18`: Ecosystem Chat real-provider/custody activation owner; portable StegGate integration is already installed there, so do not create a competing provider workstream.
- `StegVerse-Labs/Site#24`: stable endpoint publication/discovery and fail-closed routing owner.
- Render is not architectural authority.

## Automation

Active continuation surfaces:

```text
scripts/guard_steggate_session_continuity.py
.github/workflows/steggate-session-continuity.yml
.github/workflows/steggate-live-observer.yml
.github/workflows/steggate-fallback-public-runtime.yml
scripts/finalize_steggate_live_activation.py
```

The continuity worker rejects premature archive state while this goal is incomplete. The public fallback rotates unhealthy Quick Tunnels and republishes only after the full acceptance contract. The live observer/finalizer remain fail closed until issue #68's hosted API evidence can be persisted.

## Current execution inventory

Authoritative machine-readable inventory: `management/steggate-full-functional-activation.json`.

```text
FF-CONTEXT-01 COMPLETE
FF-ARCH-02 COMPLETE
FF-EXEC-03 COMPLETE
FF-SERVICE-04 COMPLETE
FF-RESIDENT-DEPLOY-05 PARTIAL
FF-OBSERVE-06 ACTIVE
FF-ACTIVATE-07 WAITING_FOR_RESIDENT_EVIDENCE
FF-PORTABLE-08 COMPLETE_AND_HOSTED_VALIDATED
FF-CONSUMER-09 COMPLETE_AND_HOSTED_VALIDATED
FF-STABLE-RENDEZVOUS-10 BLOCKED_ON_DEPLOYMENT_CREDENTIAL_BOUNDARY
```

## Exact next tasks

1. Do not reopen portable StegGate design: it is implemented and hosted validated.
2. Do not reopen the LLM consumer adapter: its portable integration proof is green and its broader provider activation remains canonically owned by `StegVerse-org/LLM-adapter#18`.
3. Continue issue #68 resident API acceptance through the stable rendezvous lane or another already-authorized stable endpoint surface; do not duplicate policy logic.
4. On a successful stable route deployment, externally verify `/health`, `/v1/self-test`, and `/v1/evaluate`, persist the observation, then allow the existing finalizer to reconcile #68.

## Blockers

```text
Stable rendezvous deployment: BLOCKED — Site Actions Cloudflare credential boundary absent at run 31286621905.
Render persistent deployment: BLOCKED — workspace build minutes exhausted; paid increase not authorized.
Portable/local StegGate: NOT BLOCKED — active and hosted validated.
Ecosystem Chat portable consumer: NOT BLOCKED — integration verified; real-provider/custody activation is separate machine-owned issue #18.
```

## Integration and propagation obligations

Do not propagate a claim that the stable resident API is active until directly observed. Portable topology and consumer integration may be referenced as validated capabilities. Site/Publisher/admissibility-wiki/StegGuardian release/publication state must follow their canonical gates; no publication authority is created here.

## Completeness

```text
developed-files: 22/22
scaffolding-or-stubs: 0
validation-groups: 8/10
integration-groups: 8/10
activation-tasks complete: 6/10
session goals transferred-or-complete: 6/10
goal activation: 60%
```

## Archive condition

NOT SATISFIED.

Do not archive the originating session while issue #68's stable/live API acceptance remains incomplete. Portable topology completion does not erase the explicitly retained resident API goal. Archive only after remaining resident/rendezvous work is completed or issue #68 is authoritatively superseded by an equivalent durable contract and no unique session role remains.
