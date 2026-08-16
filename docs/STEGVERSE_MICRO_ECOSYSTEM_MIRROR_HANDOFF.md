# StegVerse Micro-Ecosystem Mirror Handoff

## Source of truth

```text
repository: StegVerse-Labs/StegCore
canonical_branch: main
canonical_runtime_identity: stegverse:steggate:canonical:three-layer:v1
canonical_evaluator: stegcore.three_layer.evaluate_three_layer
credential_authority: TV/TVC
non-TV/TVC secret/token required: FALSE
physical_host_topology: ONE_SOVEREIGN_PHYSICAL_HOST
additional_physical_machine_required: FALSE
third_party_runtime_infrastructure_required: FALSE
```

This file owns the StegGate/AdmittedCode portable micro-ecosystem assembly, S/NS deployment definitions, portable package production, and the transition into SDK distribution / Node Sovereign activation.

Parent repository handoff: `docs/STEGCORE_MIRROR_HANDOFF.md`.

## Global single-host sovereignty invariant

Every S or NS portable deployment must remain independently operable within its declared local scope on one sovereign physical StegVerse host. A required third-party machine, VM, process host, scheduler, state host, control-plane executor, validation computer, or other third-party runtime dependency is incompatible with Sovereignty.

Independent execution proof must use same-host logical isolation when technically sufficient:

```text
ONE_SOVEREIGN_PHYSICAL_HOST
-> canonical persistent runtime
-> isolated logical process/state/identity boundaries when independent proof is required
-> restart/replay/reconstruction/isolation proof
-> temporary logical peers may terminate
-> canonical local runtime remains independently operable
```

External providers, blockchains, sites, or other nodes may be optional participants/inputs. Their absence must not disable local governance, proof verification, replay, reconstruction, or control-plane operation within the deployment's declared local scope.

Canonical executable contract:

```text
micro_ecosystem/manifest.json schema: stegverse.micro-ecosystem.manifest.v3
single_host_sovereignty.physical_host_topology: ONE_SOVEREIGN_PHYSICAL_HOST
single_host_sovereignty.independent_validation_mechanism: SAME_HOST_ISOLATED_LOGICAL_BOUNDARIES
authority_boundaries.requires_additional_physical_machine: false
authority_boundaries.requires_third_party_runtime_infrastructure: false
credential_authority: TV/TVC
non_tv_tvc_secret_or_token_allowed: false
```

`tools/run_stegverse_micro_ecosystem.py` independently validates this contract and emits `stegverse.micro-ecosystem.proof-receipt.v3`. `tools/build_portable_ecosystem_package.py` fails closed if the manifest weakens the contract and binds the contract into `PACKAGE_RECEIPT.json`.

## Completed source goal

`STEGVERSE-MICRO-ECOSYSTEM-001`

Status:

```text
SOURCE_IMPLEMENTATION: COMPLETE
HOSTED_VALIDATION: PASS
MERGED: TRUE
merge_commit: 1cdd479a8c50a61cda9a236fc05b126592362fff
source_PR: #133
single_host_sovereignty_contract: COMPLETE_VALIDATED
release_artifact_bound: FALSE
remote_SDK_download_active: FALSE
Node_Sovereign_membership_active: FALSE
```

Original implementation validation head `28a21b3319a6c6e46dd8ab3f97ca89354a7d1b35` passed all required hosted checks before merge.

### Single-host sovereignty propagation evidence

Installed commits on `main`:

```text
a3035e81d51c615b8dd1d19a70fd65d8196f6ab3  manifest v3 single-host contract
db878be4bbbe68da7383a44378282380146f338d  package receipt/builder enforcement
f5f5cc04410c72ed5059103304730f5f45d4974d  portable package fail-closed tests
72083dbcad3199ec0055ebefff6d870c30b18c5b  micro-ecosystem proof-runner contract validation
```

The first full-suite run on `f5f5cc...` correctly failed because the old proof runner still required manifest v2. That was a real compatibility defect, not suppressed validation. Commit `72083dbc...` upgraded the runner to manifest/proof v3 and strong single-host validation.

Canonical post-fix evidence:

```text
workflow: StegCore Tests - No Non-TV/TVC Credential Authority
run: 31925980402
head: 72083dbcad3199ec0055ebefff6d870c30b18c5b
conclusion: SUCCESS
```

The earlier readiness gate on the package-enforcement head also passed:

```text
workflow: Test Readiness - No Non-TV/TVC Credential Authority
run: 31925837384
head: f5f5cc04410c72ed5059103304730f5f45d4974d
conclusion: SUCCESS
```

Hosted Actions is validation only and creates no runtime, membership, credential, or sovereign-host authority.

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
physical_host_topology: ONE_SOVEREIGN_PHYSICAL_HOST
```

An S deployment is a sovereign StegVerse installation and does not claim genuine ecosystem-node membership.

### NS — StegVerse NS Ecosystem / Node Sovereign profile

```text
node_status_requested: true
node_status_self_assertable: false
ecosystem_membership_required: true
node_activation_profile: micro_ecosystem/node_sovereign_profile.v1.json
physical_host_topology: ONE_SOVEREIGN_PHYSICAL_HOST
```

Selecting or installing NS does not create Node Sovereign membership. Until genuine membership evidence exists, local proof remains:

```text
node_activation_state: PROFILE_DEFINED_NOT_ACTIVE
membership_proof_present: false
node_sovereign_active: false
```

Normative explanation: `docs/STEGVERSE_NODE_SOVEREIGN_DEFINITION.md`.

## Node Sovereign activation contract

A genuine NS deployment requires inspectable evidence for all required capabilities in `micro_ecosystem/node_sovereign_profile.v1.json`, including portable node continuity identity, local/user-controlled continuity state, shared continuity envelope, receipts, governed node exchange, independent receiver admission, authority monotonicity, externally established membership proof, anti-Sybil standing, recovery/reconstruction, privacy-bounded participation, canonical governed execution, least-stable viable execution, and contribution receipts.

Preserved invariants include:

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
physical host count != logical independence
logical independence must not require third-party infrastructure
```

## SDK-first distribution

Consumer/distribution authority belongs to:

```text
StegVerse-org/StegVerse-SDK
docs/SDK_PORTABLE_PACKAGE_CONSOLE_MIRROR_HANDOFF.md
```

Package IDs remain:

```text
stegverse-sdk-s-micro-ecosystem-v0
stegverse-sdk-ns-micro-ecosystem-v0
```

SDK install remains distinct from activation. NS install remains distinct from node admission.

## Active artifact-transport convergence / collision boundary

`STEGVERSE-PORTABLE-ARTIFACT-002` has an active release-transport implementation in PR `#137` (`feat/portable-candidate-artifact-transport-v0`). It owns version-driven artifact construction/transport for TVC and currently changes:

```text
.github/workflows/portable-release-candidate.yml
sdk/portable_package_catalog.v1.json
tests/test_portable_release_factory.py
tools/build_portable_ecosystem_package.py
tools/prepare_portable_release.py
```

Do not create a competing artifact/publication implementation. PR #137 already carries the single-host contract fields forward and advances the package receipt to `stegverse.sdk.portable-package-receipt.v3` for versioned packages. The SDK consumer has been separately updated to accept v2/v3 only under the same sovereignty checks.

At this handoff update PR #137 remains the canonical artifact-transport claimant and must reconcile/rebase current `main` before merge if GitHub still reports a merge conflict. This handoff does not transfer TVC publication authority to the current session.

## Early-adopter economics

Verified contribution accounting remains separately owned by `StegVerse-Labs/stegfin-governance` under `STEGFIN-EARLY-ADOPTER-CONTRIBUTION-001`. Package download/install, enrollment, passive holding, traffic generation, or self-declared node identity are not rewardable contribution by themselves.

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
one-host logical proof != Node Sovereign membership
third-party hosted validation != production runtime
```

No secret/token is embedded in the unit. Any protected credential use remains TV/TVC-owned.

## Completion states

```text
ASSEMBLY_INSTALLED: COMPLETE
DUAL_CLASS_IMPLEMENTED: COMPLETE
NODE_DEFINITION_CAPTURED: COMPLETE
NS_PROFILE_READY: COMPLETE
PORTABLE_PROOF_TESTED: COMPLETE
SINGLE_HOST_SOVEREIGNTY_CONTRACT: COMPLETE_VALIDATED
SDK_PACKAGE_BUILDER_INSTALLED: COMPLETE
SDK_PACKAGE_SOURCE_VALIDATED: COMPLETE
IMMUTABLE_PACKAGE_ARTIFACTS_BOUND: PENDING_ACTIVE_PR_137
SDK_REMOTE_DOWNLOAD_ACTIVE: PENDING
NODE_SOVEREIGN_ACTIVE: PENDING
RELEASED_PORTABLE_PRODUCT: PENDING
```

Do not collapse these states.

## Successor goals

### Goal A — `STEGVERSE-PORTABLE-ARTIFACT-002`

Canonical claimant: PR #137 / version-driven portable release transport. Produce exact immutable S and NS artifacts, retain hashes/receipts, and transfer permanent publication to TV/TVC without giving build transport runtime authority.

Acceptance includes exact source, deterministic ZIP+TAR.GZ, per-file receipts, archive hashes, immutable public locator, SDK locator/hash binding, SDK verification, single-host sovereignty receipt/manifest match, no provider account, and no non-TV/TVC secret.

### Goal B — `STEGVERSE-NODE-SOVEREIGN-ACTIVATION-003`

Implement genuine NS membership and continuity integration without self-accreditation and without requiring an additional physical host or third-party runtime infrastructure for the deployment itself.

## Next executable actions

1. PR #137 owner reconciles current `main` and retains the single-host contract while completing versioned candidate transport.
2. TV/TVC owns permanent publication/admission of exact artifacts; build transport has no publication authority.
3. SDK consumes the admitted immutable locators/hashes and validates download -> verify -> install for S and NS.
4. Keep Node Sovereign membership activation separate from install/profile selection.
5. At actual release/tag readiness, re-read and reconcile Site, `GCAT-BCAT-Engine/Publisher`, admissibility-wiki, and stegguardian-wiki handoffs before propagation.

## Current claim

```yaml
completed_task: STEGVERSE-MICRO-ECOSYSTEM-001 + SINGLE-HOST-SOVEREIGNTY-CONTRACT
single_host_validation_head: 72083dbcad3199ec0055ebefff6d870c30b18c5b
active_successor_goal: STEGVERSE-PORTABLE-ARTIFACT-002
canonical_artifact_transport_claim: StegVerse-Labs/StegCore#137
secondary_successor_goal: STEGVERSE-NODE-SOVEREIGN-ACTIVATION-003
claim_state: SUCCESSOR_WORK_ACTIVE_DISTINCT_OWNER
manual_competing_artifact_transport_allowed: false
credential_authority: TV/TVC
```
