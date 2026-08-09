# StegCore Mirror Handoff

## Source of truth

```text
Organization: StegVerse-Labs
Repository: StegCore
Branch: main
Active project goal ID: STEGGATE-FULL-FUNCTIONAL-ACTIVATION-001
Originating session goal: make StegGate actually functional, preserving the complete admissibility matrix and decision/execution/observation state as reconstructable reality
Canonical project owner: StegVerse-Labs/StegCore#68 + repository-native workers
Project state: PORTABLE_STEGGATE_ACTIVE / REAL_CONSUMER_INTEGRATED / RESIDENT_HTTP_IMPLEMENTED / PUBLIC_EPHEMERAL_HTTP_PROVEN / STABLE_RENDEZVOUS_MACHINE_OWNED_BLOCKED_ON_AUTHORIZED_CREDENTIALS
Originating session state: MERGED_INTO_CANONICAL_WORKSTREAM
Conversation archive allowed: YES
Project activation complete: NO
```

Read this handoff, `management/steggate-full-functional-activation.json`, `management/steggate-portable-micronode-activation.json`, `data/steggate-session-context.json`, `data/steggate-architecture-reconciliation-state.json`, Site `data/steggate-rendezvous-activation.json`, and issue #68 before changing StegGate. Live Git/workflow evidence supersedes chat summaries.

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

`decision.py` is an intentionally minimal compatibility interface, not the full engine. Do not create a competing evaluator.

## Completed canonical capabilities

### Core runtime and decision-state reconstruction

Canonical three-layer evaluation, full matrix normalization, candidate-bound REVIEW, fail-closed semantics, commit coherence, consequence inaccessibility on non-ALLOW, execution observation, divergence/bypass semantics, and complete decision-state preservation are complete and validated.

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

The public fallback workflow has run canonical StegGate through a Cloudflare Quick Tunnel and passed `/health`, exact ALLOW/DENY/REVIEW/FAIL_CLOSED `/v1/self-test`, and complete-matrix `/v1/evaluate`. Quick Tunnel is ephemeral transport, not stable identity.

Endpoint discovery now resolves candidates in this order and independently verifies canonical health before accepting any origin:

```text
1. https://stegverse.org/api/steggate      stable StegVerse rendezvous
2. https://steggate-core.onrender.com      persistent Render lane
3. verified rotating fallback registry     ephemeral public proof lane
```

Hosted StegCore validation after this discovery change:

```text
run 31289831506
job 93185008397
169 passed
133 subtests passed
artifact 9031013648
sha256 05e3ab8b56714709df24cf81f10bd1d26ebf872c58df3c371523195819693485
```

### Portable / ephemeral governed-package topology — COMPLETE

Authoritative surfaces:

```text
src/stegcore/portable_steggate.py
tests/test_portable_steggate.py
docs/STEGGATE_PORTABLE_MICRONODE.md
management/steggate-portable-micronode-activation.json
```

A `GovernedTransitionPackage` carries the canonical `AdmissibilityRequest`, package identity/hash, portable-node profile, expected reconciled-runtime profile/fingerprint, execution/coherence context, and optional expiry. The receiver instantiates a fresh short-lived micro-node from a known StegCore runtime, verifies package/runtime binding, evaluates the canonical chain, optionally crosses commit coherence, invokes a bounded consequence only after ALLOW + coherence ALLOW, emits reconstructable evidence, and terminates. Networking is optional.

Hosted evidence: run `31286273932`, job `93175594894`, `161 tests + 129 subtests`, artifact `9029913625`, digest `sha256:fd7b9a27eb18d6e4a061e7e7b507cceb6d6b10bef649e2198c08841a9e25e054`.

### Real consumer integration — COMPLETE

Canonical consumer: `StegVerse-org/LLM-adapter` / Ecosystem Chat user-LLM path.

```text
llm_adapter/steggate_portable_consumer.py
tests/test_steggate_portable_consumer.py
.github/workflows/steggate-portable-consumer.yml
receipts/steggate-portable-consumer-integration.latest.json
LLM_ADAPTER_MIRROR_HANDOFF.md
```

Hosted evidence: run `31286444819`, job `93176065654`, SUCCESS, artifact `9029971776`, digest `sha256:c555e9035d480120d36184308d165e8e0987a0765c3020a60abf0c45f425c4f4`.

The consumer maps explicit governance facts into canonical StegCore input and supplies only the bounded provider callback. Policy drift prevents the callback. No provider credential travels in the package. No public StegGate ingress is required.

## Stable rendezvous — IMPLEMENTED / MACHINE OWNED / BLOCKED

Canonical owner:

```text
StegVerse-Labs/Site#24
StegVerse-Labs/Site/data/steggate-rendezvous-activation.json
StegVerse-Labs/Site/.github/workflows/steggate-rendezvous-deploy.yml
```

Installed Site surfaces:

```text
src/steggate-rendezvous-worker.js
wrangler.steggate.jsonc
.github/workflows/steggate-rendezvous-deploy.yml
data/steggate-rendezvous-activation.json
```

Stable intended origin:

```text
https://stegverse.org/api/steggate
```

Deployment run `31286621905`, job `93176517796`, observed both required Site Actions bindings empty before Wrangler execution. The enhanced machine-owned retry workflow run `31289859109`, job `93185080182`, then confirmed the same blocker while successfully producing artifact `9031019850`, digest `sha256:259dd1747e151ff333342f4124e0814cec71523aa4f48048cc28442c526b1e41` containing the explicit blocker observation.

The rendezvous workflow is scheduled hourly at minute 41. It remains red/blocked while credentials are unavailable, emits a machine-readable observation artifact on every run, and automatically deploys plus verifies readiness/health/exact four-disposition self-test when both authorized bindings become available. On success it persists `LIVE_ACCEPTANCE_PASS` to Site's rendezvous state. No chat polling is required.

Machine-observable release condition:

```text
CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID both become non-empty in the Site Actions runtime,
OR an already-authorized endpoint-publication plane deploys the same non-authorizing rendezvous contract.
```

## Automatic final activation chain

StegCore `.github/workflows/steggate-live-observer.yml` runs hourly. After any stable route becomes healthy, it independently resolves the endpoint, verifies `/health`, exact four-disposition `/v1/self-test`, and deterministic complete-matrix `/v1/evaluate`, then invokes `scripts/finalize_steggate_live_activation.py`. Only a full PASS may create the activation receipt, reconcile durable state, comment issue #68, and close #68.

Render `srv-d9rlic2jobas73do1q6g` remains a secondary machine-owned lane. Latest inspected deploy `dep-d9ru30bl550s73dt3vf0` failed before source build because workspace build-pipeline minutes remain exhausted. Paid capacity changes are not authorized and are not required for the portable topology.

## Collision control and adjacent workstreams

- Governance remains policy/evidence authority.
- `StegVerse-Labs/ara-admissibility-interop` remains decision-state interop/schema authority.
- `StegVerse-Labs/Continuity` remains reconstruction/Continuity consumer authority.
- `StegVerse-org/LLM-adapter#18` remains the sole Ecosystem Chat real-provider/custody activation lane; do not duplicate it.
- `StegVerse-Labs/Site#24` remains stable endpoint publication/discovery owner.
- Neural micro-node governance from the originating discussion is complete and separately consolidated at `docs/NEURAL_MICRONODE_GOVERNANCE_MIRROR_HANDOFF.md`, issue #71, and `data/neural-micronode-session-inventory.json`. Do not duplicate that experimental lane.
- Render is not architectural authority.

## Current execution inventory

Authoritative machine-readable inventory: `management/steggate-full-functional-activation.json`.

```text
FF-CONTEXT-01 COMPLETE
FF-ARCH-02 COMPLETE
FF-EXEC-03 COMPLETE
FF-SERVICE-04 COMPLETE
FF-RESIDENT-DEPLOY-05 PARTIAL / MACHINE OWNED
FF-OBSERVE-06 ACTIVE / MACHINE OWNED
FF-ACTIVATE-07 WAITING_FOR_HOSTED_EVIDENCE / MACHINE OWNED
FF-PORTABLE-08 COMPLETE_AND_HOSTED_VALIDATED
FF-CONSUMER-09 COMPLETE_AND_HOSTED_VALIDATED
FF-STABLE-RENDEZVOUS-10 BLOCKED / MACHINE OWNED / HOURLY RETRY ACTIVE
```

## Session consolidation

The project remains incomplete, but the originating chat no longer owns unique execution work. All original and adjacent session requirements are implemented, completed, or durably transferred with exact owners, machine-observable release conditions, and automatic continuation paths.

```text
MERGED INTO: StegVerse-Labs/StegCore#68
ALSO OWNED BY: StegVerse-Labs/Site#24 for stable rendezvous deployment
REAL PROVIDER/CUSTODY OWNER: StegVerse-org/LLM-adapter#18
NEURAL ADJACENT GOAL: StegVerse-Labs/StegCore#71 + docs/NEURAL_MICRONODE_GOVERNANCE_MIRROR_HANDOFF.md
```

No remaining task requires information that exists only in the conversation. No manual workflow dispatch, polling, artifact copying, blocker transcription, or receipt construction is assigned to the chat/user.

## Completeness

```text
activation tasks complete: 6/10
project developed files: 24/24
scaffolding or stubs: 0
validation groups: 9/10
integration groups: 9/10
session goals transferred-or-complete: 10/10
project goal activation: 60%
session consolidation: 100%
conversation archival readiness: 100%
```

## Archive condition for originating session

SATISFIED BY DURABLE TRANSFER.

Archiving the originating conversation does not assert that the stable resident StegGate endpoint is live. It asserts only that no unique implementation, validation, integration, propagation, reconciliation, or observation responsibility remains in chat. Repository-native owners continue fail-closed until their actual activation evidence exists.

## Machine-finalized live activation

Canonical hosted functional activation is COMPLETE. The repository-native runtime recorded PASS for `/health`, exact four-disposition `/v1/self-test`, and deterministic complete-matrix `POST /v1/evaluate`.

Deployment source: `heartbeat_ephemeral_micronode`  
Activation receipt: `data/steggate-live-activation-receipt.json`  
Observation digest: `sha256:4159d510a8c8e2d941f8c5efb8355f95ce651c328b41e22abb8be7e97b799506`  
Observed at: `2026-08-09T09:14:06.578269Z`

The persistent hosted origin is healthy and was used for activation.

Issue #68 may be closed by repository automation. No chat-session execution role remains for this functional-activation goal.
