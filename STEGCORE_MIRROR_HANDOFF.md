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
STEGGATE-PORTABLE-PRODUCT-CONSISTENCY-001: COMPLETE + HOSTED VALIDATED
```

The active #70 claim remains `current-session-common-runtime-binding / CLAIMED_FOR_IMPLEMENTATION`. The completed consistency sweep does not create a second admissibility engine or modify application-specific HIL-owned Site paths.

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

Supported current-product surfaces:

```text
Python: stegcore.AdmissibilityRequest + stegcore.evaluate_admissibility
CLI:    steggate identity | self-test | evaluate | serve
HTTP:   /health | /v1/runtime-identity | /v1/capabilities | /v1/self-test | /v1/evaluate
```

All supported surfaces terminate in the same canonical evaluation composition. A CLI, browser, SDK, API route, or consumer application must not carry a parallel policy/admissibility engine and claim canonical equivalence.

Current product documentation:

```text
README.md
docs/STEGGATE_PORTABLE_PRODUCT.md
docs/STEGGATE_RUNTIME_IDENTITY_CONTRACT.md
CHANGELOG.md
```

Machine-checkable consistency and release surfaces:

```text
VERSION
pyproject.toml
src/stegcore/version.py
src/stegcore/service.py
src/stegcore/cli.py
scripts/verify_product_consistency.py
tests/test_product_consistency.py
examples/steggate_allow_request.json
scripts/release/bump_version.py
scripts/release/update_changelog.py
.github/workflows/release-bump.yml
```

Historical receipt/schema/review/constitutional versions remain independent and are not rewritten to match product version `0.2.0`.

## Consistency sweep — COMPLETE

The 2026-08-10 sweep reconciled the current product surface on `main`:

```text
VERSION + pyproject.toml + src/stegcore/version.py
  -> one portable product version: 0.2.0

src/stegcore/service.py
  -> service version derives from canonical __version__

src/stegcore/__init__.py
  -> exports current StegGate evaluation API

src/stegcore/cli.py
  -> real portable CLI replacing the legacy in-memory node demo

README.md
  -> current implemented runtime/product posture replaces stale documentation-first scaffold framing

CHANGELOG.md
  -> 0.2.0 current-product history and explicit version-domain distinction

examples/steggate_allow_request.json
  -> stranger-runnable canonical ALLOW request

docs/STEGGATE_PORTABLE_PRODUCT.md
  -> supported surfaces, semantics, compatibility rules, and source order

docs/STEGGATE_RUNTIME_IDENTITY_CONTRACT.md
  -> product-version vs contract-version distinction and consumer acceptance rules

scripts/verify_product_consistency.py
  -> drift guard across documentation, runtime identity, CLI, packaging, examples, and release automation

tests/test_product_consistency.py
  -> executable version, identity, CLI, example, and verifier checks

scripts/release/bump_version.py
  -> updates VERSION, pyproject.toml, and source __version__ as one fail-closed release operation

scripts/release/update_changelog.py
  -> duplicate-safe Unreleased promotion into one versioned release section

.github/workflows/release-bump.yml
  -> updates and commits every portable-product version surface and runs the consistency verifier before opening a release PR
```

The consistency verifier now rejects:

- missing current-product paths;
- drift among `VERSION`, package metadata, and source version;
- service-version divergence;
- canonical runtime identity/evaluator divergence;
- missing supported CLI commands;
- stale README scaffold claims;
- missing/invalid stranger-runnable example sections;
- missing `steggate` package entry point;
- release scripts/workflows that fail to manage all current product version surfaces;
- a changelog with no entry for the current product version.

Historical artifacts whose `0.1`, schema, receipt, review, or constitutional version is provenance remain unchanged by design.

## Hosted validation — COMPLETE for consistency sweep

Fresh hosted evidence after the consistency changes:

```text
StegCore Tests
run: 31454425034
head: 228923a8ea97d6986449b34283fe50dff2c3f93f
conclusion: SUCCESS
scope: expanded product consistency guard including release automation

StegCore Tests
run: 31454452751
job: 93665269287
head: 38533b0d1a8b195ff12c7dc95b658e0734006ea9
conclusion: SUCCESS
scope: runtime identity contract/product-version-domain clarification

BCAT Gate
run: 31454275378
head: dbebe6c014aaf327704fcd678d7c6ca18d6a880c
conclusion: SUCCESS
scope: product consistency test addition checkpoint
```

The final handoff reconciliation is documentation/state transfer only; it does not change the tested runtime or version semantics above.

## Functional activation — COMPLETE

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

## Runtime identity contract — COMPLETE

```text
GET /v1/runtime-identity
contract_version: stegverse.steggate.runtime-identity.v1
runtime_identity: stegverse:steggate:canonical:three-layer:v1
canonical_owner: StegVerse-Labs/StegCore
canonical_admissibility_runtime: stegcore.three_layer.evaluate_three_layer
transport_identity_authoritative: false
```

Portable product version `0.2.0` and runtime identity contract version `v1` are separate version domains. A compatible product release does not silently change the binding contract; a breaking binding change requires an explicitly versioned successor contract.

## Heartbeat transport and lease semantics

Canonical transport remains a heartbeat-owned zero-credential public tunnel. Persistent Render authority is `NONE`.

Canonical lease lineage:

```text
StegVerse-Labs/.github/control/heartbeat-subsignals.json
subsignal: steggate_transport_lease
lease_id: STEGGATE-TUNNEL-LEASE-001
lease_is_per_heartbeat: false
wall_clock_expiry_authority: false
```

A heartbeat may open, extend, hand off, or close the lease. A heartbeat epoch is not the lease lifetime. Durable carrier/reconstruction continuation remains owned by:

```text
StegVerse-Labs/.github/handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json
StegVerse-Labs/.github/control/worker-registry.json#SHWP-DURABLE-RUNTIME-ACTIVATION
```

## Four-app canonical runtime integration — ACTIVE

Canonical state:

```text
management/steggate-four-app-runtime-binding.json
```

Last durable state read during this sweep:

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

Current-state sources take precedence over review/formalism documents:

```text
docs/STEGGATE_PRODUCT_REVIEW_V4.md -> implemented network-governance architecture context
docs/STEGGATE_PRODUCT_REVIEW_V5.md -> formalism/research expansion; not a replacement for live runtime contracts
```

No v5 concept becomes runtime authority merely because it is documented. It must be implemented, validated, and admitted through canonical owner/interop boundaries.

## Version-domain rule

Keep these identities separate and internally coherent:

```text
portable package/service version
runtime identity contract version
admissibility evaluation schema version
receipt/schema artifact versions
historical release/tag versions
architecture review versions
```

Do not mechanically replace one domain's version with another.

## Remaining work and owners

```text
StegVerse-Labs/StegCore
  -> continue issue #70 without parallel evaluators
  -> do not cut a runtime product tag until applicable release authority and release gates are satisfied

StegVerse-Labs/Site + named consumer owners
  -> produce direct public/runtime evidence for Ecosystem Chat, VACC, Math Solver, and HIL

StegVerse-Labs/.github
  -> continue sovereign carrier restart/reconstruction and lease lifecycle under canonical worker ownership

On a future governed runtime product release, destination-owned propagation/reconciliation is required for:
  -> StegVerse-Labs/Site
  -> GCAT-BCAT-Engine/Publisher
  -> StegVerse-Labs/admissibility-wiki
  -> StegVerse-002/stegguardian-wiki
```

No new runtime product tag/release is claimed by this sweep. Current four-app public-direct evidence is still `0/4`, so the product-integration release objective is not terminal.

## Validation commands

```bash
pytest -q
python scripts/verify_product_consistency.py
steggate self-test
steggate evaluate examples/steggate_allow_request.json
```

## Completion

```text
functional StegGate runtime: 100%
portable product consistency implementation: 100%
portable product consistency hosted validation: 100%
runtime identity core contract: 100%
current portable-product files developed: 100%
scaffolding/stubs in current portable StegGate path: 0
four-app CI-or-stronger binding: 3/4
four-app public-direct evidence: 0/4
parent four-app goal: NOT COMPLETE
consistency-sweep session transfer: COMPLETE
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

The consistency-sweep work is fully installed, hosted-validated, and durably transferred. No unique state from this conversation is required to continue issue #70 or the machine-owned runtime-continuity work.
