# Transaction Continuity Mirror Handoff

## Source of truth

```text
organization: StegVerse-Labs
repository: StegCore
branch: feat/manifested-transaction-continuity
issue: #79
parent handoff: STEGCORE_MIRROR_HANDOFF.md
canonical runtime identity: stegverse:steggate:canonical:three-layer:v1
canonical evaluator: stegcore.three_layer.evaluate_three_layer
```

Live repository state, CI, PR state, and receipts supersede chat summaries.

## Goal

Complete the original SDK/LLM-adapter continuity purpose by ensuring demo/runtime inputs are manifested and admitted through ingestion, sent through the same canonical AdmittedCode/StegGate execution path as ordinary ecosystem runtimes, re-ingested on return, and exposed as discoverable/replayable/reconstructable transaction trajectories.

## Installed on implementation branch

```text
src/stegcore/transaction_lifecycle.py
src/stegcore/__init__.py
tests/test_transaction_lifecycle.py
tools/run_manifested_transaction_demo.py
docs/MANIFESTED_TRANSACTION_CONTINUITY.md
docs/MANSOOR_EVALUATION_BASELINE_DELTA.md
docs/TRANSACTION_CONTINUITY_MIRROR_HANDOFF.md
StegCore#79
```

## Boundary invariants

```text
manifest grants authority: false
required route: ingestion -> steggate -> return_ingestion
canonical evaluator bypass: prohibited
demo-specific evaluator: prohibited
application-specific evaluator: prohibited
bounded consequence: only after canonical StegGate ALLOW + commit coherence ALLOW
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

## Longitudinal proof cases

```text
T0: valid $420 candidate -> ALLOW -> executor invoked
T1-current-state: same candidate + policy_current=false -> DENY -> executor not invoked
T1-candidate-mutation: $4,200 candidate + prior $420 approval hash -> DENY -> executor not invoked
```

The earlier transaction remains discoverable and chain-verifiable after the later refusal.

## Mansoor evaluation boundary

Mansoor's evaluation target remains the frozen AdmittedCode / StegGate 0.2.0 branch at baseline commit `5d86d7999199b9403a05320710c4d1bb95527327`. Development continues forward. If Mansoor independently identifies this continuity deficiency, his finding remains independently attributable. Any semantic change to the canonical evaluator/runtime identity must version forward rather than mutate the frozen reference.

## Remaining work before merge

```text
1. open PR from feat/manifested-transaction-continuity to main;
2. run repository CI and inspect failures;
3. correct any implementation/test defects;
4. merge only after required checks pass;
5. update STEGCORE_MIRROR_HANDOFF.md on main with #79 completion/current state.
```

## Remaining ecosystem integration after core merge

```text
StegVerse-Labs/StegCore
  -> route packaged SDK/browser/LLM-adapter continuity-enabled callers through run_manifested_transaction;
  -> replace/deprecate residual adapter-local inline governance where still executable;
  -> define durable ecosystem discovery/index backing beyond local JSONL ledger.

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
core continuity module: IMPLEMENTED ON BRANCH
public SDK exports: IMPLEMENTED ON BRANCH
longitudinal tests: IMPLEMENTED ON BRANCH
demo runner: IMPLEMENTED ON BRANCH
Mansoor baseline delta: PRESERVED ON BRANCH
CI validation: PENDING
merge: PENDING
packaged SDK/LLM-adapter caller migration: PENDING FOLLOW-ON
durable cross-ecosystem discovery index: PENDING FOLLOW-ON
release propagation: NOT YET ELIGIBLE
```
