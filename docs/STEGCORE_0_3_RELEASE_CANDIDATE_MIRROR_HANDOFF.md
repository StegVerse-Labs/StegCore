# StegCore 0.3 Release Candidate Mirror Handoff

Updated: 2026-08-26
Repository: StegVerse-Labs/StegCore

## Purpose

Freeze the successor StegCore 0.3.0 product containing canonical SPE-standing enforcement and bounded public interlock traversal while satisfying the TVC aggregate-release source-parent contract.

Historical v0.2.0 release evidence remains historical provenance and is not moved or reused.

## Canonical product identity

```text
package: stegcore
version: 0.3.0
target_tag: v0.3.0
runtime_identity: stegverse:steggate:canonical:three-layer:v1
credential/release authority: TV/TVC
```

## Proof-critical runtime ancestry

- PR #146 canonical SPE-standing enforcement
  - merge: 26b18204b135a213231d160b718e47ca6ab46f28
- PR #148 bounded public interlock traversal
  - merge/proof-critical ancestor: 124ea6b53ff79db8f514cacf1aab295f03cacf74
  - exact validation: 32808051766 SUCCESS

The canonical runtime verifies the SDK/SPE/interlock standing bundle before consequence invocation. Missing, stale, tampered, DENY, or differently-bound standing/interlock evidence fails closed.

SPE ALLOW alone is not execution authority. StegGate ALLOW alone is not evidence that execution occurred.

## Final TVC release relation

The final immutable release relation prepared for the successor aggregate is:

```text
source_parent:
ef38410505b0ef3e84148892b1d6e3cdef20f300
  -> exactly one direct child
release_commit:
58445bb14642c1889cf9802666c15bd48c6d2e39
  -> only release-notes mutation
target_tag:
v0.3.0
```

The source parent contains the complete 0.3.0 package/version/docs/tests/workflow/handoff state. The release commit is reserved as the note-only immutable release candidate. Moving `main` is not a substitute for either coordinate.

## Exact source validation

StegCore source-parent exact-head validation:
- run `32911552882`: SUCCESS
- validates 0.3.0 package identity;
- standing/interlock runtime tests;
- canonical StegGate runtime;
- bounded public interlock traversal;
- product consistency;
- build;
- wheel metadata.

The reconciled source was later merged into canonical main at:
`788a55b8e616b53fdc593fd56a10e9d7f5625f51`

That main merge is not the release identity.

## Successor aggregate relationship

TVC successor policy binds this exact pair together with:
- SDK 1.2.0;
- Core-Lite 0.9.0;
- Master Records 0.2.0.

The exact TV authorization request warrants release commit:
`58445bb14642c1889cf9802666c15bd48c6d2e39`

The exact TV request remains `REQUESTED_NOT_GRANTED`; therefore this candidate is not yet released.

## Current state distinctions

```text
0.3.0 runtime source: IMPLEMENTED
standing/interlock behavior: VALIDATED
canonical runtime source: MERGED
release source parent: FROZEN / VALIDATED
note-only release commit: PREPARED
v0.3.0 immutable tag: NOT RELEASED
GitHub Release: NOT RELEASED
successor aggregate receipt: NOT PRODUCED
POST_RETURN production proof: NOT COMPLETE
```

## Authority boundary

```text
candidate prepared != released
source validation != release authority
PR/main merge != tag publication
release candidate != runtime activation
SPE standing != execution authority
StegGate ALLOW != execution evidence
credential/release authority: TV/TVC
```

## Remaining boundary

No further StegCore source reconciliation is required for this successor release lane.

Continuation is owned by TV/TVC successor aggregate runtime:
1. real current GRANTED authorization;
2. real resident SKAP double-interlock credential custody;
3. immutable tag/release creation or exact-existing verification;
4. verified aggregate receipt;
5. genuine SDK POST_RETURN production proof;
6. Master Records organization record + reciprocal ACK + portable verification + replay/reconstruction PASS.

StegCore PR #141 remains a separate active capability-context/transaction-lifecycle lane and is not satisfied or superseded by this 0.3 release preparation.
