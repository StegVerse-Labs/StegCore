# Manifest Receipt ID Mirror Handoff

## Authority

```text
goal_id: STEGCORE-MANIFEST-RECEIPT-ID-001
repository: StegVerse-Labs/StegCore
branch: main
parent_handoff: docs/TRANSACTION_CONTINUITY_MIRROR_HANDOFF.md
issue: #85
implementation_state: INSTALLED_UNVALIDATED
release_state: NOT_RELEASED
```

## Goal

Provide a canonical user-facing `manifest_receipt_id` that resolves to exactly one immutable governed run, returns its evidence package, supports non-mutating replay comparison, and supports historical reconstruction without re-executing consequence.

The identifier is a locator only and grants no authority.

## Installed surfaces

```text
src/stegcore/manifest_receipts.py
tests/test_manifest_receipts.py
```

Installation commits:

```text
02e15e9b0311f261742db911451e3914ad806e03  registry + replay/reconstruction contract
1c19e2cb8aafd8529f411396dc91b2653b59df92  tests
```

## Canonical semantics

`manifest_receipt_id_for(result)` derives an `MR-<SHA256>` locator from exact transaction identity, manifest hash, receipt-chain head, and canonical runtime identity.

`ManifestReceiptRegistry` is append-only and provider-neutral with optional JSONL backing. It supports:

```text
register(result)
resolve(manifest_receipt_id)
evidence_package(manifest_receipt_id)
reconstruct(manifest_receipt_id)
replay(manifest_receipt_id, replay_handler)
```

Registration requires an already verified transaction chain. Duplicate IDs with different immutable content fail closed. Unknown IDs fail closed. Replay is prohibited from claiming consequence re-execution and checks the original retained record for mutation. Reconstruction distinguishes persisted historical receipt evidence from reconstructed summary material and records `consequence_reexecuted: false`.

## Remaining production dependency

`master-records/orchestration` remains the owner for durable shared ecosystem backing and production resolution. The current registry is provider-neutral and suitable for binding to that backing, but this commit does not by itself prove production master-record service activation.

## Validation status

Implementation and tests are installed. No sovereign/local test execution receipt was produced in this change session. Do not claim COMPLETE, VALIDATED, RELEASED, or activated until the canonical validation path records evidence and master-record shared backing is bound.
