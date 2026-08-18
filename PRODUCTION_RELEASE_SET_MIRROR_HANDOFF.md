# Production Release Set Mirror Handoff

## Source of truth

```text
organization: StegVerse-Labs
repository: StegCore
canonical_branch: main
credential_authority: TV/TVC
non-TV/TVC release credential permitted: false
```

## Goal

Create a durable tagged/released governance-runtime state for evaluator provenance. Ongoing development must not change the identity of the released evaluator state.

## Validated release candidate

```text
aggregate_release_set: ODA3-EVALUATOR-PATH-2026-08-18-R1
role: governance_runtime
package: stegcore
package_version: 0.2.0
target_release_tag: v0.2.0
candidate_commit: 083557adec1bdbace09ebd10fb0765eb8e9a9d08
SDK governed-test pin matches candidate: true
current main has advanced beyond validated SDK pin: true
existing GitHub release: stegcore-v1.0-constitution (older constitutional release; not this evaluator runtime candidate)
release_notes: RELEASE_NOTES_EVALUATOR_PATH_0.2.0.md
```

## Release requirements

The StegVerse worker owning release execution must:

1. validate the exact candidate commit `083557adec1bdbace09ebd10fb0765eb8e9a9d08` used by the SDK governed-test lane;
2. create durable tag `v0.2.0` resolving exactly to that candidate; do not reuse the constitutional release tag;
3. publish the prepared release notes/changelog describing the StegGate/manifested-transaction runtime semantics present in that candidate;
4. record tag, immutable commit SHA, package version, publication time, release URL, and changelog URL;
5. propagate the completed release identity to `StegVerse-org/StegVerse-SDK` production release catalog/packet contract;
6. continue later development on moving branches/main without altering the released tag.

The newer `main` state may become a later release only after its own validation. It must not be substituted into the historical evaluator release set for runs validated against `083557...`.

## Evaluator invariant

```text
validated dependency pin determines historical release candidate
latest main does not retroactively become the tested runtime
release tag != moving branch
future releases are comparable, not substitutable
```

## Readiness evidence

The canonical StegCore handoff identifies portable product version `0.2.0`, runtime identity `stegverse:steggate:canonical:three-layer:v1`, and the canonical three-layer admissibility runtime. The SDK production-validation lane is pinned to this exact commit and retained cross-repository sovereign validation evidence for the manifested transaction route. Release publication must preserve this historical candidate rather than substitute later `main` state.

## Current executable state

```text
SOURCE_CANDIDATE: FROZEN
RELEASE_NOTES: PREPARED
TARGET_TAG: FIXED_TO_v0.2.0
TAG_PUBLICATION: PENDING_TV_TVC_RELEASE_AUTHORITY
GITHUB_ACTIONS_RUNTIME_AUTHORITY: NONE
STATUS: RELEASE_READY_AWAITING_TAG_PUBLICATION
```
