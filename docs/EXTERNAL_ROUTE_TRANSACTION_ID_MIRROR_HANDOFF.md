# External Route Transaction Identity Mirror Handoff

```text
goal_id: STEGCORE-EXTERNAL-ROUTE-TX-ID-001
repository: StegVerse-Labs/StegCore
branch: feat/external-route-transaction-id
parent_handoff: docs/TRANSACTION_CONTINUITY_MIRROR_HANDOFF.md
implementation_state: INSTALLED_PENDING_VALIDATION_MERGE
release_state: NOT_RELEASED
```

## Purpose

Allow a transaction identity established by the ecosystem manifest/ingestion carrier before StegCore entry to remain the same identity inside canonical StegCore manifested execution.

`run_manifested_transaction(..., transaction_id=...)` now passes the externally established ID into the existing `manifest_transaction(...)` function. No evaluator, governance, consequence, receipt, or authority semantics are changed.

## Invariant

```text
manifest/entry transaction_id
== ingestion/CGE transaction_id
== StegCore manifest transaction_id
== StegCore transition receipt transaction_id
== return-ingestion transaction_id
```

Supplying a transaction ID grants no authority. Canonical StegGate and commit-coherence execution remain unchanged.

## Installed surfaces

```text
src/stegcore/transaction_lifecycle.py
tests/test_external_route_transaction_id.py
docs/EXTERNAL_ROUTE_TRANSACTION_ID_MIRROR_HANDOFF.md
```

## Dependency

The evaluator production-validation lane in StegVerse-org/StegVerse-SDK and Data-Continuation/core-lite requires this identity-preserving hook so the manifested transaction does not split into an outer route transaction and a separately generated StegCore transaction.

Do not claim merged/released/evaluator-ready until repository tests and the cross-repository integrated route pass.
