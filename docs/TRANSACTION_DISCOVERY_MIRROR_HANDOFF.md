# Transaction Discovery Mirror Handoff

## Source of truth

```text
organization: StegVerse-Labs
repository: StegCore
branch: feat/transaction-discovery-shared-store-003
goal_id: TRANSACTION-DISCOVERY-SHARED-STORE-003
parent_issue: #83
worker_assist_issue: #98
role: CLAIMED_FOR_IMPLEMENTATION
canonical_runtime_authority: stegcore.steggate.evaluate_admissibility
credential_authority: TV/TVC
github_token_runtime_authority: NONE
```

This is the canonical continuation record for the remaining shared-provider slice of transaction discovery. It supplements `STEGCORE_MIRROR_HANDOFF.md` and does not modify canonical policy, execution, model/runtime, or credential authority.

## Pre-existing completed work

PR #84 merged the provider-neutral discovery/index foundation at `ee40743aba893d9e16293cb2521abe58e2abedae`. Existing completed behavior includes append-only discovery records, JSONL persistence/reload, safe summaries, reviewer lineage fields, and deterministic lookup without payload disclosure.

## Active worker-assist claim

```text
task_id: TRANSACTION-DISCOVERY-SHARED-STORE-003
claimant: current worker-assist session
claim_state: CLAIMED_FOR_IMPLEMENTATION
claim_created_at: 2026-08-14T11:23:35-05:00
claim_release_condition: shared provider implementation + tests pass hosted validation, merge to main, and #83/#98 are reconciled
collision_scope:
  - src/stegcore/transaction_discovery_store.py
  - tests/test_transaction_discovery_store.py
  - src/stegcore/__init__.py discovery-store exports only
  - docs/TRANSACTION_DISCOVERY_MIRROR_HANDOFF.md
```

Excluded collision scopes: manifold governance worker files, StegCore #70 four-app runtime binding, local-model/heartbeat activation, TV/TVC authority, deployment/release authority, and canonical StegGate decision semantics.

## Installed branch implementation

```text
src/stegcore/transaction_discovery_store.py
tests/test_transaction_discovery_store.py
src/stegcore/__init__.py
```

The provider layer adds:

1. `DiscoveryRecordStore`, a provider-neutral persistence protocol;
2. `SqliteDiscoveryStore`, a standard-library SQLite durable backing;
3. WAL mode and bounded busy timeout for independent local StegVerse processes sharing one database;
4. append-only transaction identity semantics;
5. idempotent registration only for the exact existing record/chain;
6. canonical record-hash revalidation on every read/write;
7. explicit rejection of payload-disclosure or authority-granting records;
8. indexed scalar lookup plus deterministic lineage/stage/state filtering;
9. disclosure-safe summaries;
10. no secret, token, external provider, policy evaluation, execution, or receipt-minting dependency.

## Validation commands

```text
pytest -q tests/test_transaction_discovery.py tests/test_transaction_discovery_store.py
pytest -q
python scripts/verify_product_consistency.py
```

## Remaining parent #83 work after this slice

Once this shared-store slice is validated and merged, the remaining parent issue is consumer/public discovery binding and any eventual release-facing propagation. Those must remain owned by the applicable consumer/release workstreams and cannot be claimed complete from Core storage alone.

## Archive/release condition

This claim releases after hosted validation + canonical merge + durable issue/handoff reconciliation. No Site, Publisher, admissibility-wiki, or stegguardian-wiki propagation is authorized from this provider slice alone.
