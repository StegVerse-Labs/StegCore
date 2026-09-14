# Universal Governance Sovereign Reference Runner Mirror Handoff

Updated: 2026-09-14
Repository: StegVerse-Labs/StegCore
Issue: #179
Branch: main
State: FRESH_BINDING_SOURCE_MERGED_VALIDATED / RESIDENT_EXECUTION_PENDING
Credential authority: TV/TVC
Authority effect: NONE except bounded target consequence after separate target-authority validation

## Goal

Provide the executable local-source runner consumed by `StegVerse-Labs/.github#690 / SHWP-UNIVERSAL-GOVERNANCE-ENFORCED-REFERENCE-001`.

The runner executes the already-merged Universal Governance reference path and writes only to a caller-supplied bounded state root.

## Required execution

native reference action -> thin external adapter -> Universal InTr request -> registered Governance profile -> StegCore evaluation -> exact commit-time fresh-binding check -> deterministic StegGate target-authority/credential/capability/commit gate -> bounded target mutation -> consequence evidence -> Universal InTr return -> Master Records source projection -> runner receipt

The runner does not perform Master Records destination custody. The resident `.github` worker independently invokes the locally materialized Master Records validator after this runner succeeds.

## Bound-state outputs

- target/state.json
- evidence/consequence.json
- evidence/master-records-projection.json
- receipts/material-state-transition.json
- receipts/reference-boundary.latest.json

## Fresh-binding two-route experiment

The reference target has one bounded consequence primitive with two entry paths:

1. the canonical task-runner closure used only after Governance, present-state, fresh-binding, and StegGate commit coherence;
2. an alternate consequence-capable route that reaches the same target primitive but cannot supply the canonical boundary permit.

The experiment establishes `V0/P0/E0`, obtains the initial Governance ALLOW, then performs a separately retained material fixture transition to `V1/P1/E1` before any consequence executes. The original V0 binding therefore returns DENY and does not invoke the executor. The alternate route is attempted against the same changed state and also leaves consequence state unchanged.

The exact candidate is then re-evaluated and a new V1 commit binding is derived. Only that current binding may proceed to the existing `execute_external_consequence_if_coherent()` path. After the one allowed consequence, its `execution_binding_id` is consumed. Replay through the alternate route returns DENY and the target mutation count remains exactly one.

The reusable source predicate lives at `src/stegcore/fresh_commit_binding.py`. It compares only exact binding state and consumption state. It is not policy, Governance authority, credential authority, or execution authority and cannot invoke a consequence itself.

Bound fields are:

- state_version
- state_hash
- policy_epoch
- policy_hash
- evidence_bundle_hash
- execution_binding_id

Missing required observed state or missing consumption state is `FAIL_CLOSED`; established drift or reuse is `DENY`.

## Validation and merge evidence

```text
StegCore PR: #217
validated head: 0ac4ec3e352a24b009b9dc0e6b85ff72d0d6a477
merge commit: 7cbef555608f7e154ae575dcbd5b4e65fbf0c85c
Universal Governance Connector Runtime: run 34896699738 SUCCESS
StegCore Package Version Identity Validation: run 34896699800 SUCCESS
StegVerse 001/002 Validator: run 34896699757 SUCCESS
BCAT required context: run 34896699748 SKIPPED because repository is private under the credentialless anonymous-source BCAT contract
```

The BCAT workflow now materializes its required `bcat-check` context on pull requests. On private repositories the job is explicitly skipped; that skip is not BCAT validation evidence and grants no authority. The credentialless lane still performs anonymous-source validation only when public source is available.

## Required final receipt fields

The v2 reference receipt retains, at minimum:

- initial and post-transition state identity;
- initial and fresh Governance receipt hashes;
- initial and fresh binding hashes;
- material-state-transition receipt hash;
- stale canonical route disposition with executor_invoked=false;
- stale alternate route disposition with executor_invoked=false;
- fresh binding check matrix;
- governed execution/coherence receipt hash;
- post-commit alternate-route replay disposition with executor_invoked=false;
- final_target_mutation_count=1;
- consequence evidence and Universal InTr return lineage;
- reference_enforced_boundary_observed=true within the bounded runner receipt;
- alternate_consequence_path_closed=true;
- stale_binding_rejected=true;
- fresh_binding_required=true;
- fresh_binding_single_use=true;
- real_external_system_enforced_activation=false;
- resident_execution_observed=false.

## Authority and proof boundaries

```text
fresh commit binding ALLOW != Governance authority
fresh commit binding ALLOW != target authority
Governance ALLOW != target authority
adapter != execution authority
Interlock/InTr/HB != execution authority
GitHub Actions != runtime authority
credential authority = TV/TVC
repository writeback = false
Continuity minting = false
publication authority = false
```

Source tests and GitHub Actions prove deterministic software behavior only. They do not establish resident WorkerCoordinator claim/fence, resident execution, reference-boundary observation on the sovereign resident, Master Records destination custody for an authentic resident instance, or real external-system ENFORCED activation.

## Lifecycle

- FRESH_BINDING_SOURCE_IMPLEMENTED: true
- SOURCE_VALIDATED: true at PR #217 exact head
- MERGED: true at `7cbef555608f7e154ae575dcbd5b4e65fbf0c85c`
- RESIDENT_EXECUTION_OBSERVED: false
- REFERENCE_ENFORCED_BOUNDARY_OBSERVED: false
- MASTER_RECORDS_AUTHENTIC_RESIDENT_CUSTODY: false
- REAL_EXTERNAL_SYSTEM_ENFORCED_ACTIVATION: false
