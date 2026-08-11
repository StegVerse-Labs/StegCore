# StegCore Mirror Handoff

## Source of truth

```text
organization: StegVerse-Labs
repository: StegCore
branch: main
canonical StegGate owner: StegVerse-Labs/StegCore
portable product version: 0.2.0
canonical runtime identity: stegverse:steggate:canonical:three-layer:v1
canonical admissibility runtime: stegcore.three_layer.evaluate_three_layer
```

This file is the canonical continuation source for current StegCore runtime, product, validation, and integration work. Live repository/workflow evidence supersedes chat summaries.

## Current goals

```text
STEGGATE-FULL-FUNCTIONAL-ACTIVATION-001 / issue #68: COMPLETE
STEGGATE-HEARTBEAT-CREDENTIAL-INTEGRATION-001 / issue #75: COMPLETE
STEGGATE-TUNNEL-CONTINUITY-HARDENING: MACHINE-OWNED CONTINUATION
STEGGATE-FOUR-APP-RUNTIME-BINDING-001 / issue #70: ACTIVE
STEGGATE-PORTABLE-PRODUCT-CONSISTENCY-001: IMPLEMENTED; CI OBSERVATION PENDING
```

The active #70 claim remains `current-session-common-runtime-binding / CLAIMED_FOR_IMPLEMENTATION`. The consistency sweep does not create a second admissibility engine or modify application-specific HIL-owned Site paths.

## Canonical authority chain

```text
Governance policy/evidence
  -> src/stegcore/three_layer.py:evaluate_three_layer
  -> src/stegcore/steggate.py:evaluate_admissibility
  -> ALLOW | DENY | REVIEW | FAIL_CLOSED
  -> src/stegcore/steggate_runtime.py:governed_steggate_execute
  -> src/stegcore/commit_governance.py:coherence_gate
  -> bounded consequence only after ALLOW + coherence ALLOW
  -> observation / reconciliation
```

Transport discovery, heartbeat cadence, leases, UI state, CLI state, provider state, and application integration do not grant policy or execution authority.

## Portable product boundary — 0.2.0

Current supported product surfaces:

```text
Python: stegcore.AdmissibilityRequest + stegcore.evaluate_admissibility
CLI:    steggate identity | self-test | evaluate | serve
HTTP:   /health | /v1/runtime-identity | /v1/capabilities | /v1/self-test | /v1/evaluate
```

All supported surfaces terminate in the same canonical evaluation composition. A CLI, browser, SDK, API route, or consumer application must not carry a parallel policy/admissibility engine and claim canonical equivalence.

Canonical current-product documentation:

```text
README.md
docs/STEGGATE_PORTABLE_PRODUCT.md
docs/STEGGATE_RUNTIME_IDENTITY_CONTRACT.md
CHANGELOG.md
```

Canonical machine-checkable consistency surfaces:

```text
VERSION
pyproject.toml
src/stegcore/version.py
scripts/verify_product_consistency.py
tests/test_product_consistency.py
examples/steggate_allow_request.json
```

Historical receipt/schema/review/constitutional versions remain independent and are not rewritten to match product version `0.2.0`.

## Consistency sweep — 2026-08-10

Completed on `main`:

```text
src/stegcore/version.py          -> canonical package/service version source
VERSION                           -> 0.2.0
pyproject.toml                    -> 0.2.0 + steggate console entry point
src/stegcore/service.py           -> SERVICE_VERSION derives from __version__
src/stegcore/__init__.py          -> exports current StegGate evaluation API
src/stegcore/cli.py               -> real portable product CLI; legacy demo removed
README.md                         -> current runtime/product posture replaces scaffold framing
CHANGELOG.md                      -> 0.2.0 product history and version-domain distinction
examples/steggate_allow_request.json -> stranger-runnable canonical request
docs/STEGGATE_PORTABLE_PRODUCT.md -> concise supported-surface/compatibility contract
scripts/verify_product_consistency.py -> drift guard
tests/test_product_consistency.py -> version, identity, CLI, example, verifier tests
```

The verifier checks:

- current-product path existence;
- `VERSION`, package metadata, and source-version equality;
- service version derivation from the source version;
- canonical runtime identity and evaluator identity;
- required CLI commands;
- absence of stale README scaffold claims;
- presence/shape of the canonical example request;
- installed `steggate` console entry point.

This sweep deliberately did **not** rewrite historical artifacts whose `0.1`, schema, receipt, review, or constitutional version is part of their provenance.

## Functional activation — complete

Issue #68 is closed. Canonical first activation was merged through PR #74 / commit:

```text
1d26a21354917a74b40a6c8f1101d91e8d2c44c0
```

Historical activation evidence:

```text
data/steggate-live-activation-receipt.json
state: COMPLETE
deployment_source: heartbeat_ephemeral_micronode
observed_at: 2026-08-09T09:14:06.578269Z
```

That receipt proves the recorded activation event. It is not a continuously rewritten health record.

## Runtime identity contract — complete

```text
GET /v1/runtime-identity
contract_version: stegverse.steggate.runtime-identity.v1
runtime_identity: stegverse:steggate:canonical:three-layer:v1
canonical_owner: StegVerse-Labs/StegCore
canonical_admissibility_runtime: stegcore.three_layer.evaluate_three_layer
transport_identity_authoritative: false
```

Direct validation already recorded before this sweep:

```text
workflow: StegCore Tests
run: 31338809707
job: 93308982069
conclusion: SUCCESS
artifact: 9045154237
artifact digest: sha256:e59d08fc0de1a4c4fdf893c5db1d857e20fe7e3fa77dc3cde44c1e6f4b2f6ab2
```

The 2026-08-10 consistency commits triggered fresh repository CI; do not count those new runs as successful until their hosted conclusions are observed.

## Heartbeat transport and lease semantics

Canonical transport remains a heartbeat-owned zero-credential public tunnel. Persistent Render authority is `NONE`.

Canonical lease:

```text
StegVerse-Labs/.github/control/heartbeat-subsignals.json
subsignal: steggate_transport_lease
lease_id: STEGGATE-TUNNEL-LEASE-001
state last recorded in this handoff lineage: OPEN
lease_is_per_heartbeat: false
wall_clock_expiry_authority: false
```

A heartbeat may open, extend, hand off, or close the lease. A heartbeat epoch is not the lease lifetime. Release occurs through explicit CLOSE, accepted successor handoff, or completion of all declared lease-dependent tasks under the canonical lifecycle rules.

Durable org-level continuation remains owned by:

```text
StegVerse-Labs/.github/handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json
StegVerse-Labs/.github/control/worker-registry.json#SHWP-DURABLE-RUNTIME-ACTIVATION
```

## Four-app canonical runtime integration — active

Canonical state file:

```text
management/steggate-four-app-runtime-binding.json
```

Last durable state read for this sweep:

```text
core contract: COMPLETE
applications CI-bound or stronger: 3/4
applications public-direct: 0/4
Ecosystem Chat: CI_BOUND_PUBLIC_EVIDENCE_PENDING
VACC: CI_BOUND_PUBLIC_EVIDENCE_PENDING
Math Solver: CI_BOUND_PUBLIC_EVIDENCE_PENDING
HIL: PENDING_DIRECT_EVIDENCE
```

Issue #70 remains open until each named application retains direct evidence that its governed path consumed the canonical runtime identity and traversed canonical StegGate semantics. Static contract existence is not four-app completion.

Collision boundaries:

- do not modify HIL upload paths owned by the separate Site claimant;
- do not create per-application StegGate evaluators;
- do not make an ephemeral/vendor URL part of canonical runtime identity.

## Architecture and research documents

Use current-state sources before review/formalism documents.

```text
docs/STEGGATE_PRODUCT_REVIEW_V4.md -> implemented network-governance architecture context
docs/STEGGATE_PRODUCT_REVIEW_V5.md -> formalism/research expansion; does not replace live runtime contracts
```

No v5 concept becomes runtime authority merely because it is documented. It must be implemented, validated, and admitted through the canonical owner/interop boundaries.

## Version-domain rule

The following are intentionally distinct:

```text
portable package/service version
runtime identity contract version
admissibility evaluation schema version
receipt/schema artifact versions
historical release/tag versions
architecture review versions
```

Do not mechanically replace one domain's version with another. Product consistency means each domain is internally coherent and its authority is explicit.

## Remaining work

```text
StegVerse-Labs/StegCore
  -> observe fresh CI caused by the 0.2.0 consistency sweep
  -> correct any test/BCAT failure before claiming validated consistency
  -> continue #70 without parallel evaluators

StegVerse-Labs/Site + named consumer owners
  -> produce direct public/runtime evidence for Ecosystem Chat, VACC, Math Solver, HIL

StegVerse-Labs/.github
  -> continue sovereign carrier restart/reconstruction and lease lifecycle under canonical worker ownership

Release/propagation destinations after a governed runtime product release is actually authorized:
  -> StegVerse-Labs/Site
  -> GCAT-BCAT-Engine/Publisher
  -> StegVerse-Labs/admissibility-wiki
  -> StegVerse-002/stegguardian-wiki
```

No new runtime product tag/release is claimed by this sweep. A release requires successful fresh hosted evidence plus the applicable release authority and destination-owned propagation review.

## Validation

Local/repository commands:

```bash
pytest -q
python scripts/verify_product_consistency.py
steggate self-test
steggate evaluate examples/steggate_allow_request.json
```

Required release evidence:

```text
full test suite PASS
BCAT/repository governance gates PASS
product consistency verifier PASS
four-disposition self-test PASS
canonical example request -> ALLOW
runtime identity unchanged or explicitly versioned successor
```

## Completion

```text
functional StegGate runtime: 100%
portable product consistency implementation: 100%
portable product consistency hosted validation: PENDING OBSERVATION
runtime identity core contract: 100%
four-app CI-or-stronger binding: 3/4
four-app public-direct evidence: 0/4
scaffolding/stubs in current portable StegGate product path: 0
historical/legacy substrate: preserved, non-authoritative for current product behavior
parent four-app goal: NOT COMPLETE
archive readiness for active #70 parent goal: NO
```

## Canonical continuation

```text
StegVerse-Labs/StegCore#70
StegVerse-Labs/Site#239
StegVerse-Labs/StegCore/STEGCORE_MIRROR_HANDOFF.md
StegVerse-Labs/StegCore/docs/STEGGATE_PORTABLE_PRODUCT.md
StegVerse-Labs/StegCore/management/steggate-four-app-runtime-binding.json
StegVerse-Labs/.github/handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json
```
