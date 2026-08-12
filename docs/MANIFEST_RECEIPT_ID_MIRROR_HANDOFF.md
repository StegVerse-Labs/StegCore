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

`manifest_receipt_provider.py` installs the shared-backing contract. `build_master_records_submission()` promotes the exact run identity into the Master Records manifest-receipt custody envelope, while `MasterRecordsManifestReceiptProvider` validates custody, evidence retrieval, and reconstruction responses without selecting credentials/providers or granting authority.

## Full custody before caller projection

The SDK/LLM-adapter manifest may request caller-facing return projection modes `ALL`, `SELECTED`, or `NONE`. StegCore must treat those as post-governance disclosure/egress preferences, not as transition-recording authority.

Required ordering:

```text
canonical manifested transaction
-> canonical governance/state transitions
-> complete exact-run result + receipt chain
-> canonical manifest_receipt_id
-> retain full canonical evidence package in Master Records shared backing
-> apply caller return projection (ALL | SELECTED | NONE)
-> return permitted caller-facing result
```

Mandatory invariant:

```text
caller_return_projection_cannot_change_canonical_run_identity: true
caller_return_projection_cannot_suppress_master_records_custody: true
caller_return_projection_cannot_erase_transition_history: true
```

`NONE` therefore means no transition-detail projection to the caller. It does not mean the transition chain is absent from the canonical run or Master Records backing.

## Shared backing progress

`master-records/orchestration` has installed and composed the exact-run custody surface into its canonical deployment target:

```text
services/manifest_receipt_custody.py
services/manifest_receipt_custody_api.py
services/canonical_custody_app.py
tests/test_manifest_receipt_custody.py
tests/test_manifest_receipt_custody_api.py
tests/test_canonical_custody_app.py
render-custody.yaml -> services.canonical_custody_app:app
MANIFEST_RECEIPT_CUSTODY_MIRROR_HANDOFF.md
```

The canonical Master Records deployment surface contains the authenticated manifest-receipt POST/GET/reconstruction routes. Exact-run immutability, fail-closed conflicts, evidence retrieval, reconstruction, and non-authority semantics remain preserved.

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
[done] Master Records exact-run API primitives installed
[done] Master Records exact-run routes composed into canonical custody deployment target
[done] full-custody-before-caller-projection invariant recorded
```

## Worker continuation boundary

Do not create another receipt-ID algorithm, local authority store, custody service, or parallel evaluator. Remaining StegCore work is integration proof:

```text
1. connect `MasterRecordsManifestReceiptProvider` to an admitted transport for the canonical Master Records custody deployment;
2. prove one canonical ID resolves to one immutable retained run through that transport;
3. prove full canonical evidence retention occurs before caller projection;
4. prove ALL/SELECTED/NONE caller projection cannot change run identity or Master Records custody;
5. prove replay leaves the retained original unchanged and never re-executes consequence;
6. prove reconstruction distinguishes persisted historical evidence from reconstructed summary material;
7. expose the same provider contract to SDK and LLM-adapter callers;
8. run canonical sovereign/local validation and record inspectable PASS evidence;
9. only then update `docs/TRANSACTION_CONTINUITY_MIRROR_HANDOFF.md` and issue #85 completion state.
```

## Activation boundary

Shared backing and canonical route composition are installed, but `master-records/orchestration` remains repository-wide activation-blocked pending its existing persistent-storage, backup/restore, and live-authenticated round-trip readiness evidence. This StegCore handoff must not convert installed backing into a production-activation claim.

## Validation status

Implementation and tests are installed. No sovereign/local test execution receipt was produced in this change session. Do not claim COMPLETE, VALIDATED, RELEASED, or activated until the canonical validation path records evidence and shared backing integration is proven.
