# Transaction Continuity Mirror Handoff

## Source of truth

```text
organization: StegVerse-Labs
repository: StegCore
branch: main
issue #79: COMPLETE
PR #80: MERGED / c227547b1d1e7ce4cce3b8b13c2212ed50a0f116
issue #81: COMPLETE
PR #82: MERGED / 04425f592ab2b7bfbd0181fac8511d14b8b08048
parent handoff: STEGCORE_MIRROR_HANDOFF.md
canonical runtime identity: stegverse:steggate:canonical:three-layer:v1
canonical evaluator: stegcore.three_layer.evaluate_three_layer
```

Live repository state, CI, PR state, and receipts supersede chat summaries.

## Goal

Complete the original SDK/LLM-adapter continuity purpose by ensuring demo/runtime inputs are manifested and admitted through ingestion, sent through the same canonical AdmittedCode/StegGate execution path as ordinary ecosystem runtimes, re-ingested on return, and exposed as discoverable/replayable/reconstructable transaction trajectories.

## Installed and merged

```text
src/stegcore/transaction_lifecycle.py
src/stegcore/__init__.py
tests/test_transaction_lifecycle.py
tools/run_manifested_transaction_demo.py
docs/MANIFESTED_TRANSACTION_CONTINUITY.md
docs/MANSOOR_EVALUATION_BASELINE_DELTA.md
docs/TRANSACTION_CONTINUITY_MIRROR_HANDOFF.md
core/llm_adapter.py
tests/test_legacy_llm_adapter_canonicalization.py
StegCore#79
StegCore#81
```

## Boundary invariants

```text
manifest grants authority: false
required route: ingestion -> steggate -> return_ingestion
canonical evaluator bypass: prohibited
demo-specific evaluator: prohibited
application-specific evaluator: prohibited
bounded consequence: only after canonical StegGate ALLOW + commit coherence ALLOW
legacy prompt-only LLM adapter ALLOW fallback: REMOVED
historical receipts: immutable
Mansoor 0.2.0 evaluation reference: immutable
```

## Implemented transaction chain

```text
external input
  -> SDK manifestation
  -> MANIFEST_ADMITTED receipt
  -> governed_steggate_execute
  -> ALLOW | DENY | REVIEW | FAIL_CLOSED transition receipt
  -> bounded executor only when governance + coherence allow
  -> RESULT_INGESTED receipt
  -> SDK result bundle
  -> discover / verify_chain / reconstruct / replay descriptor
```

Each transition receipt carries sequence, stage/state, processor identity, predecessor receipt hash, input/output state hashes where available, decision reference, routing fields, details, and canonical receipt hash.

## Legacy LLM adapter canonicalization

`core/llm_adapter.py` is now compatibility-only for prompt classification and historical Triad-shaped candidate construction. Those objects explicitly carry no admissibility authority.

```text
legacy evaluate_action(prompt-only)
  -> shape/persist candidate for audit
  -> FAIL_CLOSED / canonical_admissibility_request_required

legacy evaluate_manifested_action(explicit AdmissibilityRequest)
  -> run_manifested_transaction
  -> ingestion
  -> canonical StegGate + commit coherence
  -> return ingestion
  -> replayable/reconstructable result
```

The old adapter-local inline evaluator that could mint ALLOW when no external validator was available has been removed.

## Longitudinal proof cases

```text
T0: valid $420 candidate -> ALLOW -> executor invoked
T1-current-state: same candidate + policy_current=false -> DENY -> executor not invoked
T1-candidate-mutation: $4,200 candidate + prior $420 approval hash -> DENY -> executor not invoked
```

The earlier transaction remains discoverable and chain-verifiable after the later refusal.

## Validation evidence

PR #80 required workflows all passed before merge:

```text
Validate StegCore Runtime: success
StegCore Tests: success
Test Readiness: success
Validate StegVerse 001 002 Baseline: success
BCAT Gate: success
```

PR #82 required workflows all passed before merge:

```text
Validate StegCore Runtime: success
StegCore Tests: success
Test Readiness: success
Validate StegVerse 001 002 Baseline: success
BCAT Gate: success
```

## Mansoor evaluation boundary

Mansoor's evaluation target remains the frozen AdmittedCode / StegGate 0.2.0 branch at baseline commit `5d86d7999199b9403a05320710c4d1bb95527327`. Development continued forward without modifying that branch. If Mansoor independently identifies this continuity deficiency, his finding remains independently attributable. Any semantic change to the canonical evaluator/runtime identity must version forward rather than mutate the frozen reference.

## Remaining ecosystem integration

```text
StegVerse-Labs/StegCore
  -> define durable ecosystem discovery/index backing beyond local/in-process or JSONL ledger;
  -> bind packaged SDK/browser consumer surfaces to transaction discovery where continuity envelopes are required;
  -> preserve finding -> evidence -> replay -> remediation -> verification lineage for reviewer findings.

StegVerse-Labs/Site
  -> consume canonical transaction identity/trajectory for public application proof.

GCAT-BCAT-Engine/Publisher
  -> publish/reconcile transaction continuity contract when release criteria are met.

StegVerse-Labs/admissibility-wiki
  -> document manifested continuity/replay/reconstruction semantics after release authority.

StegVerse-002/stegguardian-wiki
  -> document discoverability-versus-disclosure and guardian-facing reconstruction semantics after release authority.
```

## Completion status

```text
core continuity module: 100% MERGED
public SDK exports: 100% MERGED
longitudinal tests: 100% MERGED
demo runner: 100% MERGED
legacy LLM-adapter parallel ALLOW escape removal: 100% MERGED
legacy manifested canonical path: 100% MERGED
Mansoor baseline delta preservation: 100%
CI validation: 100% PASS
core merge: 100%
durable cross-ecosystem discovery index: NEXT INTEGRATION GOAL
release propagation: NOT YET ELIGIBLE
```
