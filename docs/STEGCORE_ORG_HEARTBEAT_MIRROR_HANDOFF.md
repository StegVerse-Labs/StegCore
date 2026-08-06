# StegCore Organization Heartbeat Mirror Handoff

## Authority

This handoff governs only the organization-heartbeat claimant adapter in `StegVerse-Labs/StegCore`. The canonical repository handoff remains `docs/STEGCORE_MIRROR_HANDOFF.md` for repository-wide state.

## Goal

```text
goal_id: STEGCORE-ORG-HEARTBEAT-001
issue: StegVerse-Labs/StegCore#50
branch: main
state: RETURN_COMMITTED_PENDING_CENTER_ACCEPTANCE
```

## Installed surfaces

```text
scripts/produce_org_heartbeat_return.py
.github/workflows/org-heartbeat-return.yml
tests/test_org_heartbeat_adapter.py
data/org-heartbeat/TASK-2026-0003-1.json
```

## Completed work

- claimant adapter merged through PR #51 at `df5ff834fad2785bbb0a63fae91b2d51b7a91786`;
- scoped organization claim received for `TASK-2026-0003` with fencing token `1`;
- center assertion `TASK-2026-0003-1.json` received with epoch `1` and nonce `7c3ca3c29d8f4ab5a2ab78e45a945d01`;
- deterministic counter-assertion committed at `data/org-heartbeat/TASK-2026-0003-1.json`;
- returned artifact preserves claims, scope, policy version, fencing token, and explicit non-authority fields.

## Collision boundary

This work does not modify the external-evidence, metered-platform, proof-anchor, decision-bridge, or governed-runtime surfaces owned by other active workstreams.

## Authority boundary

The heartbeat return is testimony and evidence, not a Continuity receipt. It grants no execution, release, publication, custody, or receipt-minting authority.

## Validation

Static deterministic comparison requirements:

```text
nonce match
same epoch
same claim set
same scope
same policy version
same fencing token
execution_authority=false
release_authority=false
continuity_receipt_minted=false
```

## Remaining machine-owned action

`StegVerse-Labs/.github` must accept the committed return, emit a `stegverse.org-heartbeat-observation/v1` record with `deterministic_ok=true`, close `TASK-2026-0002` and `TASK-2026-0003`, and release the scoped claim.

## Archive condition

This adapter workstream is archive-safe after the center observation and claim release are committed in `StegVerse-Labs/.github`.
