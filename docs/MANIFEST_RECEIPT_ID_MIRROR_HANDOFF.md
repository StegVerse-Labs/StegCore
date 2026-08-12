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
src/stegcore/manifest_receipt_provider.py
tests/test_manifest_receipts.py
tests/test_manifest_receipt_provider.py
```

Installation commits:

```text
02e15e9b0311f261742db911451e3914ad806e03  registry + replay/reconstruction contract
1c19e2cb8aafd8529f411396dc91b2653b59df92  registry tests
729bd52382a9ef0a67bcce91514dc390e230e8a9  Master Records provider contract
1968ca420d2e0d7d21754f57584f379ccdf31c7f  provider contract tests
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

`manifest_receipt_provider.py` now installs the shared-backing contract. `build_master_records_submission()` promotes the exact run identity into the Master Records manifest-receipt custody envelope, while `MasterRecordsManifestReceiptProvider` validates custody, evidence retrieval, and reconstruction responses without selecting credentials/providers or granting authority.

## Shared backing progress

`master-records/orchestration` has installed the exact-run custody and authenticated HTTP primitives required by this provider:

```text
services/manifest_receipt_custody.py
services/manifest_receipt_custody_api.py
tests/test_manifest_receipt_custody.py
tests/test_manifest_receipt_custody_api.py
MANIFEST_RECEIPT_CUSTODY_MIRROR_HANDOFF.md
```

Those surfaces preserve one receipt ID -> one immutable retained run, fail closed on conflicting bindings, expose evidence retrieval/reconstruction, and do not grant execution/admissibility authority.

## Completed handoff tasks

```text
[done] canonical MR-<SHA256> identifier semantics
[done] append-only local/provider-neutral registry
[done] evidence package retrieval
[done] replay receipt semantics with original immutability check
[done] reconstruction receipt semantics without consequence re-execution
[done] Master Records submission serialization contract
[done] explicit shared-backing provider interface
[done] shared-backing authority-boundary verification tests installed
```

## Worker continuation boundary

Do not create another receipt-ID algorithm, local authority store, or parallel evaluator. Remaining work is integration proof:

```text
1. connect `MasterRecordsManifestReceiptProvider` to an admitted transport for the installed Master Records manifest-receipt API;
2. prove one canonical ID resolves to one immutable retained run through that shared backing;
3. prove replay leaves the retained original unchanged and never re-executes consequence;
4. prove reconstruction distinguishes persisted historical evidence from reconstructed summary material;
5. expose the same provider contract to SDK and LLM-adapter callers;
6. run canonical sovereign/local validation and record inspectable PASS evidence;
7. only then update `docs/TRANSACTION_CONTINUITY_MIRROR_HANDOFF.md` and issue #85 completion state.
```

## Activation boundary

Shared backing primitives are installed, but `master-records/orchestration` remains repository-wide activation-blocked pending its existing persistent-storage, backup/restore, and live-authenticated round-trip readiness evidence. This StegCore handoff must not convert installed backing into a production-activation claim.

## Validation status

Implementation and tests are installed. No sovereign/local test execution receipt was produced in this change session. Do not claim COMPLETE, VALIDATED, RELEASED, or activated until the canonical validation path records evidence and shared backing integration is proven.
