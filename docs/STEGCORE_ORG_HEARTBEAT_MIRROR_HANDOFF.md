# StegCore Organization Heartbeat Mirror Handoff

## Authority

This handoff governs only the organization-heartbeat claimant adapter in `StegVerse-Labs/StegCore`. The canonical repository handoff remains `docs/STEGCORE_MIRROR_HANDOFF.md` for repository-wide state.

## Goal

```text
goal_id: STEGCORE-ORG-HEARTBEAT-001
issue: StegVerse-Labs/StegCore#50
branch: feat/org-heartbeat-claimant-adapter
state: IMPLEMENTED_ON_BRANCH_NOT_MERGED
```

## Installed surfaces

```text
scripts/produce_org_heartbeat_return.py
.github/workflows/org-heartbeat-return.yml
tests/test_org_heartbeat_adapter.py
```

## Behavior

The adapter consumes a `stegverse.org-heartbeat/v1` assertion for `StegVerse-Labs/StegCore`, rejects repository mismatch, echoes the nonce and epoch, returns the declared claim, scope, policy version, and fencing token, binds the current repository commit as evidence, and emits explicit non-authority fields.

## Collision boundary

This work does not modify:

```text
src/stegcore/external_evidence.py
tests/test_external_evidence.py
scripts/verify_governance_external_evidence_contract.py
contracts/governance_external_evidence_snapshot/
.github/workflows/external-evidence-interop.yml
src/stegcore/metered_platform.py
open PR surfaces owned by #15, #17, #24, or #27
```

## Non-claims

- no organization claim has yet been granted to StegCore;
- no center-issued nonce has yet completed a round trip;
- the workflow artifact is not a Continuity receipt;
- the adapter grants no execution, release, publication, custody, or receipt-minting authority;
- merge-time fencing is not yet a required repository rule.

## Validation

```text
pytest -q tests/test_org_heartbeat_adapter.py
```

## Completion condition

The adapter is complete only after its pull request merges, a center assertion is delivered to the workflow, the returned artifact is validated by `StegVerse-Labs/.github`, and the organization handoff records the matched round trip.

## Next action

Open and review the adapter pull request. After merge, register a scoped organization claim for the adapter surfaces and perform the first nonce-bound heartbeat round trip.
