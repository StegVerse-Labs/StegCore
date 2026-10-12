# StegCore post-0.3.0 source and release reconciliation — issue #240

Status: SOURCE_RECONCILED / RELEASE_NOT_AUTHORIZED / SUCCESSOR_VERSION_NOT_ASSIGNED
Inspected main baseline: `74a4876b8f5023d0d32c39761148b029cf897091`
Goal issue: https://github.com/StegVerse-Labs/StegCore/issues/240

## Immutable release lineage

The frozen TVC 0.3.0 source parent is `ef38410505b0ef3e84148892b1d6e3cdef20f300`, and its release-notes-only direct child is `58445bb14642c1889cf9802666c15bd48c6d2e39`. These coordinates are authoritative for the historical TVC candidate per `docs/STEGCORE_0_3_RELEASE_CANDIDATE_MIRROR_HANDOFF.md` and issue #155. The later `282f30e9e46efc3a8d0d867f48e08c3aa6534e22` mentioned in issue #203 and its propagation handoff is a descendant, **not** the frozen note-only release commit. GitHub compare of `58445bb...282f30e9` returned 74 commits ahead, zero behind. Do not retarget a frozen release to that descendant.

## Post-freeze source inventory

GitHub compare `ef384105...74a4876` returned **133 commits ahead, zero behind**. The compare includes substantial new or modified source: `authority_basis.py`, `current_basis.py`, `fresh_commit_binding.py`, `gadi.py`, `external_governance_adapter.py`, `universal_governance_connector.py`, `commit_governance.py`, `steggate_runtime.py`, `three_layer.py`, `transaction_lifecycle.py`, and `manifest_receipt_provider.py`, plus corresponding tests and schemas. These are not merely documentation/CI changes. The Master Records wire contract update `e5f6da6f` introduces organization-record names with legacy acceptance aliases. Compatibility of the entire 133-commit change set has **not** been mechanically established by this comparison.

## Version identity decision

Current `VERSION`, `pyproject.toml`, and `src/stegcore/version.py` all equal `0.3.0`; README agrees; `CHANGELOG.md` contains an `[Unreleased]` section. Existing frozen 0.3.0 candidate identity must not be rewritten. Because the post-freeze source has new public functionality and potentially material contract changes, a **new successor release candidate is required before distributing current main as the frozen 0.3.0 product**. Whether the successor is `0.3.1`, `0.4.0`, or another approved version depends on a compatibility audit and Task Registry/TVC release authority. No speculative version bump is made.

## Machine-checkable invariants

- `VERSION == pyproject.toml project.version == stegcore.version.__version__ == 0.3.0` for this source line.
- Frozen 0.3.0 TVC source parent and release commit remain unchanged.
- Historical #203 release-target instruction is superseded by the exact TVC candidate relation; do not publish from 282f30e9.
- Source reconciliation is not proof of a GitHub tag, GitHub Release, PyPI distribution, resident runtime, Master Records state transition, or commercial license.
- New successor release and TVC publication authority are separate tasks and may not be inferred from this documentation-only merge.

## Disposition

ALLOW: document and correct the contradictory release-target instructions.
FAIL_CLOSED: any publication/tag/release/version transition absent authentic TV/TVC approval, exact compatibility checks, and independent release evidence.
