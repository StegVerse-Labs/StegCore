# StegCore 0.3 Release Candidate Mirror Handoff

Updated: 2026-08-25
Repository: `StegVerse-Labs/StegCore`

## Purpose

Freeze a successor StegCore release candidate containing canonical SPE-standing enforcement and bounded public interlock traversal without altering or relabeling historical `v0.2.0`.

## Historical release boundary

`PRODUCTION_RELEASE_SET_MIRROR_HANDOFF.md` remains authoritative for historical `v0.2.0` and its candidate `083557adec1bdbace09ebd10fb0765eb8e9a9d08`.

This lane is separate and successor-only.

## Candidate coordinates

```text
package: stegcore
version: 0.3.0
target_tag: v0.3.0
sdk_executable_source_commit: 124ea6b53ff79db8f514cacf1aab295f03cacf74
release_preparation_parent: ec349be317cea0593e787f53935c22876bac636a
release_candidate_commit: PENDING_EXACT_PR_MERGE
release_notes: RELEASE_NOTES_0_3_0.md
credential_authority: TV/TVC
```

The frozen SDK 1.2.0 successor candidate already pins StegCore executable source `124ea6b...`. Git comparison from `124ea6b...` to `ec349be...` shows only package-version validation metadata/documentation changes and no `src/` changes. Therefore the successor aggregate's StegCore executable/source coordinate must remain `124ea6b...`; `ec349be...` is only the release-preparation parent.

The executable source contains:

```text
PR #146 / canonical SPE-standing enforcement
feature head: f09eb36abcd3b317f35638e5c0b0c4a802d0aecf
merge: 26b18204b135a213231d160b718e47ca6ab46f28

PR #148 / bounded public interlock traversal
merge: 124ea6b53ff79db8f514cacf1aab295f03cacf74
```

Release-preparation metadata then advanced at:

```text
post-0.2 identity repair: ec349be317cea0593e787f53935c22876bac636a
runtime source changed between 124ea6b... and ec349be...: FALSE
```

## Required successor capability

```text
capability_id: STEGCORE_SPE_STANDING_BINDING_V1
feature_commit_sha: f09eb36abcd3b317f35638e5c0b0c4a802d0aecf
required containment: feature commit ancestor-or-equal to exact v0.3.0 release coordinate
```

## Evidence caveat retained

PR #146 is merged. Hosted exact-head validation exists. At the time this candidate was prepared, no canonical TVC resident private-source admission receipt for exact #146 head `f09eb36...` had been observed in repository-retained TVC state.

That missing evidence remains an open evidence item and may not be inferred from merge or release status.

## Release conditions

Before the successor aggregate release can become READY:

1. this exact release-candidate head must pass package/runtime/artifact validation;
2. its merge commit becomes the immutable StegCore `release_commit_sha` candidate;
3. TVC successor candidate must set `source_parent_commit_sha=124ea6b...` and the exact release commit;
4. SDK governed-test StegCore pin must equal `124ea6b...`;
5. installed SDK wheel alignment must PASS against the successor receipt;
6. TV/TVC guarded release execution must verify capability containment and immutable tag/release evidence.

## Authority boundary

```text
candidate prepared != released
PR merged != tag published
hosted CI != TV/TVC release authority
release candidate != runtime activation
credential authority: TV/TVC
```
