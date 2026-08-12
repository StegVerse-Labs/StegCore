# Manifested Transaction Continuity

## Purpose

StegGate governs whether a proposed consequential transition is currently admissible. This continuity layer makes the transaction itself discoverable, replayable, and reconstructable across the SDK/ingestion/governance/return path.

The manifest is **not authority**. It declares identity, provenance, routing intent, hashes, and the canonical runtime expected to evaluate the transaction. Execution authority remains exclusively with the existing StegGate + commit-coherence path.

## Canonical path

```text
external input
  -> SDK manifestation
  -> ingestion receipt
  -> canonical AdmissibilityRequest
  -> stegcore.steggate_runtime.governed_steggate_execute
       -> stegcore.steggate.evaluate_admissibility
       -> stegcore.three_layer.evaluate_three_layer
       -> commit coherence
       -> bounded consequence only after ALLOW + coherence ALLOW
  -> return-ingestion receipt
  -> SDK result bundle
  -> discovery / reconstruction / replay descriptor
```

No demo-specific evaluator, disposition injection, bypass, or alternate policy engine is permitted.

## Transaction identity

Every manifested transaction receives a durable `transaction_id` plus:

- input hash;
- canonical candidate hash;
- full request hash;
- declared route;
- source and subject;
- canonical runtime identity;
- canonical evaluator identity;
- manifest hash.

The manifest field `manifest_grants_authority` is always `false`.

## Transition receipts

Each state transition emits a hash-chained receipt containing:

- transaction identity;
- monotonic sequence number;
- stage and state;
- processor identity;
- predecessor receipt hash;
- input/output state hashes where available;
- decision-state reference where applicable;
- route origin and destination;
- transition details;
- canonical receipt hash.

The initial implementation records three mandatory stages:

```text
0 ingestion          / MANIFEST_ADMITTED
1 steggate           / ALLOW | DENY | REVIEW | FAIL_CLOSED
2 return_ingestion   / RESULT_INGESTED
```

Additional ecosystem processors may extend the chain, but they must not rewrite existing receipts.

## Discoverability versus disclosure

Discoverability means an authorized ecosystem component can locate the transaction identity and continuity trajectory. It does not imply universal payload disclosure. Hashes, state classifications, route references, and receipt identities can remain discoverable while deeper evidence is separately access-controlled.

## Replayability

The result bundle includes a `ReplayDescriptor` binding:

- transaction ID;
- manifest hash;
- request hash;
- canonical runtime identity;
- receipt-chain head;
- receipt count;
- expected disposition;
- whether the executor was invoked.

A replay consumer can rerun the retained request against the preserved runtime/version and compare stable decision semantics without treating time-bound hashes as semantic equality requirements.

## Reconstructability

`TransactionLedger.reconstruct(transaction_id)` emits the ordered state trajectory and verifies the receipt chain. Reconstruction therefore answers what processors and states the transaction traversed without relying on an application narrative.

## Eduardo longitudinal boundary test

The canonical demonstration uses ordinary manifested transactions rather than privileged fixtures:

1. T0: manifest and ingest a valid $420 candidate; canonical StegGate returns ALLOW and consequence executes.
2. T1a: retain the candidate but make policy/delegation/evidence/validity state stale; canonical StegGate refuses consequence.
3. T1b: mutate the candidate to $4,200 while retaining the original approval binding; candidate binding fails and consequence is refused.
4. Preserve both historical chains and reconstruct them independently.

The proof is not merely `ALLOW -> DENY`. It is that prior validity remains independently discoverable and replayable while present execution authority is separately refused.

## Mansoor evaluation compatibility

Mansoor's preserved AdmittedCode / StegGate 0.2.0 evaluation branch remains immutable. This continuity work is a forward additive integration around the reviewed evaluator. The reviewed baseline must never be rewritten to imply these later continuity surfaces were present at evaluation freeze.

If Mansoor independently identifies the absence of this transaction envelope, that finding remains fully attributable to his evaluation even if the forward correction is already underway.

## Public SDK surface

The package exports:

```python
TransactionManifest
TransitionReceipt
ReplayDescriptor
ManifestedTransactionResult
TransactionLedger
manifest_transaction
run_manifested_transaction
```

`run_manifested_transaction` is the common path for demos/tests that need full transaction continuity. It calls the same `governed_steggate_execute` used by ordinary governed runtime integration.

## Acceptance conditions

The boundary is considered installed when tests prove:

- manifests cannot bypass ingestion;
- manifests do not grant authority;
- an ordinary ALLOW traverses ingestion -> canonical StegGate -> return ingestion;
- a current-state change refuses consequence while preserving the earlier transaction chain;
- candidate mutation invalidates prior approval binding;
- receipt chains verify and reconstruct;
- no parallel evaluator is introduced.
