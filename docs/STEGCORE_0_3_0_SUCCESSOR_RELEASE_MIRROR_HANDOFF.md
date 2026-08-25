# StegCore 0.3.0 Successor Release Mirror Handoff

## Goal

Freeze a release-candidate commit for StegCore 0.3.0 without altering the already validated executable governance source.

```text
goal_id: STEGCORE-0.3.0-SUCCESSOR-RELEASE-001
repository: StegVerse-Labs/StegCore
branch: release/stegcore-0.3.0-successor
state: SOURCE_CANDIDATE_PENDING_HOSTED_VALIDATION
executable_source_parent: 124ea6b53ff79db8f514cacf1aab295f03cacf74
canonical_runtime_identity: stegverse:steggate:canonical:three-layer:v1
release_authority: TV/TVC
```

## Release-only mutation boundary

This lane may change package/service version identity, changelog, release notes, and this handoff only. It must not modify `standing_binding.py`, `steggate_runtime.py`, three-layer evaluation, commit governance, or the public interlock traversal proof.

## Candidate identity

```text
package: stegcore
version: 0.3.0
intended_tag: v0.3.0
release_notes: RELEASE_NOTES_0.3.0.md
```

## Required validation

- `scripts/verify_product_consistency.py` PASS;
- canonical standing/interlock regression lane PASS on exact head;
- package/version/service identities all equal `0.3.0`;
- no credential or release authority introduced.

## Completion boundary

Merge of the release-candidate source is not a release. Actual release requires the TV/TVC successor aggregate-release policy, immutable tag/release publication, capability-containment proof for `STEGCORE_SPE_STANDING_BINDING_V1`, and retained aggregate receipt.
