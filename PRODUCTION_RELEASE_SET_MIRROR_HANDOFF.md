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
role: governance_runtime
package: stegcore
package_version: 0.2.0
candidate_commit: 083557adec1bdbace09ebd10fb0765eb8e9a9d08
SDK governed-test pin matches candidate: true
current main at handoff creation: 716667e80b1b99ebbcec84ac6dabc5e3d24e4c33
current main has advanced beyond validated SDK pin: true
existing GitHub release: stegcore-v1.0-constitution (older constitutional release; not this evaluator runtime candidate)
```

## Release requirements

The StegVerse worker owning release execution must:

1. validate the exact candidate commit `083557adec1bdbace09ebd10fb0765eb8e9a9d08` used by the SDK governed-test lane;
2. create a new durable release tag resolving exactly to that candidate; do not reuse the constitutional release tag;
3. publish release notes/changelog describing the StegGate/manifested-transaction runtime semantics present in that candidate;
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

## Remaining executable work

```text
OWNER: StegVerse release worker / TV-TVC governed release authority
TASK: validate candidate, tag, publish release/changelog, propagate receipt to SDK
STATUS: READY_FOR_RELEASE_EXECUTION
```
