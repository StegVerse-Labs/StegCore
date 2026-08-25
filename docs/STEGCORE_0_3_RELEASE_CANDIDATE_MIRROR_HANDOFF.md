# StegCore 0.3 Release Candidate Mirror Handoff

Updated: 2026-08-25  
Repository: `StegVerse-Labs/StegCore`

## Purpose

Freeze the successor StegCore 0.3.0 product containing canonical SPE-standing enforcement and bounded public interlock traversal while satisfying the actual TVC aggregate-release source-parent contract.

## Historical release boundary

`PRODUCTION_RELEASE_SET_MIRROR_HANDOFF.md` remains authoritative for historical `v0.2.0`. This lane is successor-only and does not move or reuse historical tags.

## Canonical product identity

```text
package: stegcore
version: 0.3.0
target_tag: v0.3.0
runtime_identity: stegverse:steggate:canonical:three-layer:v1
credential/release authority: TV/TVC
```

All current product identity surfaces must agree on 0.3.0:

- `pyproject.toml`
- `VERSION`
- `src/stegcore/version.py`
- `README.md`
- `docs/STEGGATE_PORTABLE_PRODUCT.md`
- `CHANGELOG.md`

## Proof-critical executable ancestry

The 0.3.0 product contains:

```text
PR #146 / canonical SPE-standing enforcement
feature head: f09eb36abcd3b317f35638e5c0b0c4a802d0aecf
merge: 26b18204b135a213231d160b718e47ca6ab46f28

PR #148 / bounded public interlock traversal
proof-critical executable ancestor: 124ea6b53ff79db8f514cacf1aab295f03cacf74
```

`124ea6b...` remains an important executable/proof ancestor. It is NOT the final TVC `source_parent_commit_sha` merely because the runtime source originated there.

## TVC exact release relation

The generic TVC aggregate-release executor verifies an exact relation:

```text
source_parent_commit_sha
  -> exactly one commit
  -> release commit
  -> only changed file = declared release_notes_path
```

Therefore the canonical 0.3.0 release is prepared in two states:

1. **release source parent** — contains the complete 0.3.0 package/version/docs/tests/workflow/handoff state and contains no `RELEASE_NOTES_0_3_0.md` file;
2. **release commit** — direct child of that source parent adding only `RELEASE_NOTES_0_3_0.md`.

The exact source-parent and release SHAs are recorded after those immutable commits exist. Moving `main` may not be substituted for either coordinate.

## Required validation

The exact release source state must pass the existing `StegCore Package Version Identity Validation` workflow with:

```text
exact PR head checkout
0.3.0 identity tests
SPE standing binding tests
canonical StegGate runtime tests
bounded public interlock traversal tests
scripts/verify_product_consistency.py
wheel/sdist build
built metadata Version: 0.3.0
```

Hosted CI remains non-authorizing. It grants no tag, release, runtime, publication, credential, standing, or custody authority.

## Standing and consequence boundary

When `declared_execution_context.standing_required=true`, the canonical path verifies the SDK→SPE envelope and SPE standing receipt, preserves participant/package/transition/run identity, requires current ALLOW standing, then applies canonical StegGate admissibility and commit coherence before any bounded consequence. Missing, stale, tampered, DENY, or differently-bound standing/interlock evidence fails closed before the consequence executor.

SPE ALLOW alone never authorizes execution. StegGate ALLOW alone never proves execution occurred.

## Downstream successor aggregate

After exact StegCore source validation and the note-only release relation are proven:

1. SDK 1.2.0 `governed-test` must pin the exact TVC source-parent coordinate used by the aggregate receipt;
2. TVC successor aggregate policy must bind the exact StegCore source-parent and release commit;
3. TV/TVC guarded execution must publish/verify the immutable tag/release;
4. the aggregate receipt must then feed the SDK POST_RETURN production proof;
5. bounded consequence, Master Records custody, reciprocal ACK, portable verification, replay, and reconstruction remain separate evidence gates.

## Authority boundary

```text
candidate prepared != released
source validation != release authority
PR merge != tag publication
release candidate != runtime activation
SPE standing != execution authority
StegGate ALLOW != execution evidence
credential/release authority: TV/TVC
```
