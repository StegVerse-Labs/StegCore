# Transaction Discovery Mirror Handoff

## Source of truth

```text
organization: StegVerse-Labs
repository: StegCore
branch: main
goal_id: TRANSACTION-DISCOVERY-SHARED-STORE-003
parent_issue: #83
worker_assist_issue: #98 CLOSED_COMPLETED
pull_request: #103 MERGED
merge_commit: f8402f5a5f0d9a65825b2a97ce992c63ceaf5117
role: COMPLETE_RELEASED
canonical_runtime_authority: stegcore.steggate.evaluate_admissibility
credential_authority: TV/TVC
github_token_runtime_authority: NONE
```

This is the canonical continuation record for transaction-discovery persistence and the completed shared-provider slice. It supplements `STEGCORE_MIRROR_HANDOFF.md` and creates no policy, execution, credential, publication, or release authority.

## Provider-neutral foundation — complete

PR #84 merged the original discovery/index foundation at `ee40743aba893d9e16293cb2521abe58e2abedae` with append-only discovery records, JSONL persistence/reload, deterministic lookup, safe summaries, and reviewer finding/remediation/verification lineage without payload disclosure.

## Shared-provider slice — complete/released

```text
task_id: TRANSACTION-DISCOVERY-SHARED-STORE-003
claim_state: COMPLETE_RELEASED
claim_created_at: 2026-08-14T11:23:35-05:00
claim_released_at: 2026-08-14T11:27:09-05:00
release_basis:
  - PR #103 merged to main
  - all five hosted StegCore validation gates passed
  - issue #98 closed completed
  - parent #83 updated with remaining-scope reconciliation
```

Canonical files:

```text
src/stegcore/transaction_discovery.py
src/stegcore/transaction_discovery_store.py
tests/test_transaction_discovery.py
tests/test_transaction_discovery_store.py
src/stegcore/__init__.py
```

The shared provider layer adds:

1. `DiscoveryRecordStore`, a provider-neutral persistence protocol;
2. `SqliteDiscoveryStore`, a standard-library SQLite durable backing;
3. WAL mode, FULL synchronous durability, and bounded busy timeout for independent local StegVerse processes sharing one database;
4. append-only transaction identity semantics;
5. idempotent registration only for an exact existing record and chain;
6. canonical record-hash validation on every read/write;
7. rejection of payload-disclosure or authority-granting records;
8. indexed scalar lookup plus deterministic lineage/stage/state filtering;
9. disclosure-safe summaries;
10. no external provider, secret/token, policy evaluation, execution, or receipt-minting dependency.

## Hosted validation evidence

PR #103 head `1b04c20d25c6c05df1e78cddb564e9203bf38b5a` passed:

```text
StegCore Tests: 31819283641 SUCCESS
Validate StegCore Runtime: 31819283591 SUCCESS
BCAT Gate: 31819283575 SUCCESS
Test Readiness: 31819283597 SUCCESS
Validate StegVerse 001 002 Baseline: 31819283595 SUCCESS
```

PR #103 was then squash-merged to `main` as `f8402f5a5f0d9a65825b2a97ce992c63ceaf5117`.

## Collision/authority boundaries

The completed provider does not modify manifold governance, four-app runtime binding (#70), local-model/heartbeat activation, TV/TVC authority, canonical StegGate decisions, deployment/release authority, or disclosure policy. No NON-TV/TVC secret/token is required or accepted.

## Remaining parent #83 work

The Core persistence/provider requirements are now complete. Parent #83 remains open only for:

```text
consumer/public discovery binding
  owner: applicable Site/public consumer integration workstream
  completion: direct consumer proof that discovery uses the canonical shared/index contract without payload disclosure or authority escalation

eventual release-facing propagation
  owners: Site / Publisher / admissibility-wiki / stegguardian-wiki under their release gates
  completion: applicable source release/tag criteria admit propagation
```

Those consumer/release tasks are separate integration scopes and are not implied complete by Core storage.

## Validation commands

```text
pytest -q tests/test_transaction_discovery.py tests/test_transaction_discovery_store.py
pytest -q
python scripts/verify_product_consistency.py
```

## Completion inventory

```text
provider-neutral discovery/index: COMPLETE
shared durable backing/provider: COMPLETE
shared-provider hosted validation: 5/5 PASS
shared-provider merge: COMPLETE
scaffolding/stubs in provider slice: 0
missing required Core provider files: 0
worker-assist claim: COMPLETE_RELEASED
parent consumer/public binding: OPEN_SEPARATE_INTEGRATION_SCOPE
```

## Archive condition

The shared-provider worker-assist claim is complete and released. No chat session needs to retain this source collision scope. Parent #83 continuation is the consumer/public integration and eventual release-gated propagation described above.
