# StegVerse Micro-Ecosystem Mirror Handoff

## Source of truth

```text
repository: StegVerse-Labs/StegCore
canonical_branch: main
canonical_runtime_identity: stegverse:steggate:canonical:three-layer:v1
canonical_evaluator: stegcore.three_layer.evaluate_three_layer
credential_authority: TV/TVC
non-TV/TVC secret/token required: FALSE
```

This file owns the StegGate/AdmittedCode portable micro-ecosystem assembly, S/NS deployment definitions, portable package production, and the transition into SDK distribution / Node Sovereign activation.

Parent repository handoff: `docs/STEGCORE_MIRROR_HANDOFF.md`.

## Completed source goal

`STEGVERSE-MICRO-ECOSYSTEM-001`

Status:

```text
SOURCE_IMPLEMENTATION: COMPLETE
HOSTED_VALIDATION: PASS
MERGED: TRUE
merge_commit: 1cdd479a8c50a61cda9a236fc05b126592362fff
source_PR: #133
release_artifact_bound: FALSE
remote_SDK_download_active: FALSE
Node_Sovereign_membership_active: FALSE
```

Required hosted checks on the exact implementation head `28a21b3319a6c6e46dd8ab3f97ca89354a7d1b35` completed successfully before merge:

```text
Test Readiness - No Non-TV/TVC Credential Authority: SUCCESS
StegCore Tests - No Non-TV/TVC Credential Authority: SUCCESS
BCAT Gate - No Non-TV/TVC Credential Authority: SUCCESS
Validate StegVerse 001 002 Baseline - No Non-TV/TVC Credential Authority: SUCCESS
Validate StegCore Runtime - No Non-TV/TVC Credential Authority: SUCCESS
```

## Installed portable unit

```text
micro_ecosystem/manifest.json
micro_ecosystem/node_sovereign_profile.v1.json
sdk/portable_package_catalog.v1.json
tools/run_stegverse_micro_ecosystem.py
tools/build_portable_ecosystem_package.py
tests/test_stegverse_micro_ecosystem.py
tests/test_portable_ecosystem_package.py
docs/STEGVERSE_NODE_SOVEREIGN_DEFINITION.md
docs/STEGVERSE_SDK_PORTABLE_DISTRIBUTION.md
examples/steggate_allow_request.json
```

The portable unit reuses the canonical StegCore evaluator. It creates no parallel policy authority, execution authority, or continuity-minting authority.

## Mandatory implementation choice

No portable implementation has an implicit default.

### S — StegVerse S Ecosystem / Sovereign

```text
isolated: true
individually_operated: true
node_status_requested: false
ecosystem_membership_required: false
```

An S deployment is a sovereign StegVerse installation and does not claim genuine ecosystem-node membership.

### NS — StegVerse NS Ecosystem / Node Sovereign profile

```text
node_status_requested: true
node_status_self_assertable: false
ecosystem_membership_required: true
node_activation_profile: micro_ecosystem/node_sovereign_profile.v1.json
```

Selecting or installing NS does not create Node Sovereign membership. Until genuine membership evidence exists, local proof remains:

```text
node_activation_state: PROFILE_DEFINED_NOT_ACTIVE
membership_proof_present: false
node_sovereign_active: false
```

Normative explanation: `docs/STEGVERSE_NODE_SOVEREIGN_DEFINITION.md`.

## Node Sovereign activation contract

A genuine NS deployment requires inspectable evidence for all required capabilities in `micro_ecosystem/node_sovereign_profile.v1.json`, including:

1. portable node continuity identity;
2. local/user-controlled continuity state or vault;
3. shared continuity envelope;
4. artifact/event receipts;
5. governed node-to-node exchange;
6. independent receiver admission;
7. authority monotonicity;
8. externally established membership proof;
9. anti-Sybil standing;
10. recovery/reconstruction;
11. selective privacy-bounded participation;
12. canonical governed-execution boundary;
13. least-stable viable execution;
14. contribution receipts.

Preserved invariants:

```text
sender admission != receiver admission
downstream authority may narrow, never silently broaden
temporal adjacency != continuity
identity equality != continuity
process persistence != continuity
reconstruction alone != continuity
admissibility != continuity
node membership != execution authority
micro-node execution != sovereign node status
continuity must not become surveillance
```

## SDK-first distribution

Canonical package production is installed in this repository. Consumer/distribution console work is now active in:

```text
StegVerse-org/StegVerse-SDK
workstream: SDK-PORTABLE-PACKAGE-CONSOLE-001
PR: #34
handoff: docs/SDK_PORTABLE_PACKAGE_CONSOLE_MIRROR_HANDOFF.md
```

Package IDs:

```text
stegverse-sdk-s-micro-ecosystem-v0
stegverse-sdk-ns-micro-ecosystem-v0
```

Product progression:

```text
SDK_EARLY_ACCESS
-> SDK_COMMUNITY
-> APP_PRODUCT_CANDIDATE
-> PAID_PRODUCT_CANDIDATE
```

SDK package install must remain distinct from activation. NS install must remain distinct from node admission.

## Early-adopter economics

Verified contribution accounting is separately owned by:

```text
StegVerse-Labs/stegfin-governance
workstream: STEGFIN-EARLY-ADOPTER-CONTRIBUTION-001
```

Package download/install, enrollment, passive holding, traffic generation, or self-declared node identity are not rewardable contribution by themselves.

## Authority boundary

```text
portable unit != policy authority
portable unit != execution authority
portable unit != continuity minting
SDK install != activation
S sovereign isolation != ecosystem node membership
NS profile/install != ecosystem node membership
NS membership != policy authority
NS membership != execution authority
transport identity != authority
proof PASS != external release authorization
```

No secret/token is embedded in the unit. Any protected credential use remains TV/TVC-owned.

## Completion states

```text
ASSEMBLY_INSTALLED: COMPLETE
DUAL_CLASS_IMPLEMENTED: COMPLETE
NODE_DEFINITION_CAPTURED: COMPLETE
NS_PROFILE_READY: COMPLETE
PORTABLE_PROOF_TESTED: COMPLETE
SDK_PACKAGE_BUILDER_INSTALLED: COMPLETE
SDK_PACKAGE_SOURCE_VALIDATED: COMPLETE
MERGED: COMPLETE
IMMUTABLE_PACKAGE_ARTIFACTS_BOUND: PENDING
SDK_REMOTE_DOWNLOAD_ACTIVE: PENDING
NODE_SOVEREIGN_ACTIVE: PENDING
RELEASED_PORTABLE_PRODUCT: PENDING
```

Do not collapse these states.

## Successor goals

### Goal A — `STEGVERSE-PORTABLE-ARTIFACT-002`

Produce exact immutable S and NS package artifacts from merged source, retain archive hashes/receipts, and bind them into the SDK catalog so public SDK download can become real rather than descriptive.

Acceptance:

```text
exact merged source identified
S archive produced deterministically
NS archive produced deterministically
per-file receipt retained
archive SHA-256 retained
immutable public artifact locator retained
SDK catalog binds exact locator + archive hash
SDK verifies downloaded archive
no provider account required
no non-TV/TVC secret required
```

### Goal B — `STEGVERSE-NODE-SOVEREIGN-ACTIVATION-003`

Implement genuine NS membership and continuity integration without self-accreditation.

Acceptance begins with destination-owned bindings for portable node identity/vault/envelope, peer exchange, independent receiver admission, membership/anti-Sybil evidence, recovery, and Node Sovereign activation receipt.

## Next executable actions

1. Finish and merge SDK PR #34 after its focused portable-package tests pass.
2. Select a credential-free immutable artifact publication mechanism for Goal A; do not substitute mutable `latest` URLs or private authenticated artifacts.
3. Bind exact S/NS artifacts into the SDK download catalog and validate download -> verify -> install.
4. Begin Node Sovereign membership/continuity integration under Goal B.
5. Continue StegFin provisional contribution accounting separately; do not grant token/coin/authority from installation.
6. At actual release/tag readiness, reconcile Site, `GCAT-BCAT-Engine/Publisher`, admissibility-wiki, and stegguardian-wiki under their own handoffs.

## Current claim

```yaml
completed_task: STEGVERSE-MICRO-ECOSYSTEM-001
completed_commit: 1cdd479a8c50a61cda9a236fc05b126592362fff
active_successor_goal: STEGVERSE-PORTABLE-ARTIFACT-002
secondary_successor_goal: STEGVERSE-NODE-SOVEREIGN-ACTIVATION-003
claim_state: SUCCESSOR_WORK_ACTIVE
manual_execution_allowed: true
credential_authority: TV/TVC
```
