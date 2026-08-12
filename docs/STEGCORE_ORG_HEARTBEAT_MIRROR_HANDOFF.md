# StegCore Organization Heartbeat Mirror Handoff

## Authority

This handoff governs the organization-heartbeat claimant adapter and the non-authorizing repository-heartbeat federation adapter in `StegVerse-Labs/StegCore`. The canonical repository handoff remains `docs/STEGCORE_MIRROR_HANDOFF.md` for repository-wide state.

## Goals

```text
organization goal: STEGCORE-ORG-HEARTBEAT-001
organization issue: StegVerse-Labs/StegCore#50
organization state: RETURN_COMMITTED_PENDING_CENTER_ACCEPTANCE
repository federation goal: REPO-HEARTBEAT-FEDERATION-001
repository federation owner: StegVerse-Labs/.github#81
branch: main
```

## Installed surfaces

```text
scripts/produce_org_heartbeat_return.py
.github/workflows/org-heartbeat-return.yml
tests/test_org_heartbeat_adapter.py
data/org-heartbeat/TASK-2026-0003-1.json
.stegverse/repo-heartbeat.json
```

## Completed organization-heartbeat work

- claimant adapter merged through PR #51 at `df5ff834fad2785bbb0a63fae91b2d51b7a91786`;
- scoped organization claim received for `TASK-2026-0003` with fencing token `1`;
- center assertion `TASK-2026-0003-1.json` received with epoch `1` and nonce `7c3ca3c29d8f4ab5a2ab78e45a945d01`;
- deterministic counter-assertion committed at `data/org-heartbeat/TASK-2026-0003-1.json`;
- returned artifact preserves claims, scope, policy version, fencing token, and explicit non-authority fields.

## Repository-heartbeat federation enrollment

Commit `b7cbd49f2cede01ec81fd5e397eaa4f9912b2257` installs `.stegverse/repo-heartbeat.json` as StegCore's bounded enrollment descriptor for the central `StegVerse-Labs/.github` repository-federation layer. It declares:

```text
repo_id: stegcore
participant_class: RUNTIME
runtime_id: stegcore-runtime
canonical handoff: docs/STEGCORE_MIRROR_HANDOFF.md
required dependencies: tvc, continuity
credential_authority: TV/TVC
heartbeat_grants_execution_authority: false
github_token_required: false
central owner: StegVerse-Labs/.github#81
```

This descriptor does not create a scheduler, heartbeat daemon, credential path, or execution authority. It is input to the central single-heartbeat federation contract. A fresh runtime manifest/coverage receipt has not yet been emitted, so StegCore must not yet be counted as a healthy live repository-federation participant.

## Collision boundary

The new descriptor does not modify external-evidence, metered-platform, proof-anchor, decision-bridge, governed-runtime, or organization-heartbeat claimant implementation surfaces owned by other workstreams.

## Authority boundary

Heartbeat returns and repository federation manifests are testimony/evidence. They grant no execution, release, publication, custody, credential, deployment, or receipt-minting authority. TV/TVC remains credential authority; GitHub tokens are not a production heartbeat requirement.

## Validation

Organization-return deterministic comparison requirements remain:

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

Repository-federation validation is owned centrally by `StegVerse-Labs/.github#81` using `stegverse.repo-heartbeat-manifest/v0.1`; missing/stale/invalid required signals fail closed.

## Remaining machine-owned actions

1. `StegVerse-Labs/.github` accepts the committed organization return, emits the deterministic observation, closes `TASK-2026-0002` and `TASK-2026-0003`, and releases the old scoped organization claim.
2. The central repository-federation lane consumes the StegCore descriptor from a locally materialized StegCore repository, produces a fresh identity/runtime-bound manifest, and includes it in a real resident-heartbeat coverage receipt.
3. If StegCore runtime state cannot support a fresh `RUNTIME` signal, the central coverage remains fail-closed rather than downgrading the requirement silently.

## Archive condition

The historical organization-heartbeat adapter workstream is archive-safe after center observation/claim release. The new repository-federation enrollment is a separate machine-owned continuation at `StegVerse-Labs/.github#81` and is not complete until live coverage evidence exists.
