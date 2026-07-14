# StegCore Mirror Handoff

## Purpose

This is the current repository-local continuation source for StegCore. Future work must continue from this file without requiring prior chat context.

## Current Goal

```text
Goal: implement and automatically validate StegCore admissibility runtime behavior
Repository: StegVerse-Labs/StegCore
Activation state: runtime_candidate_implemented
Completion class: automated_runtime_validation_pending
Manual action requirement: none_for_validation_initiation
Source of truth: repository-local docs, runtime code, tests, workflows, and linked Governance contract
```

## Confirmed Repository Boundary

StegCore decides whether actions are permitted given already-resolved continuity, policy, authority, evidence, and state-integrity facts.

StegCore does not verify or mint Continuity receipts, store identity, replace StegID, or create execution authority merely by producing a decision result.

## Built Runtime Surfaces

```text
src/stegcore/decision.py
src/stegcore/runtime.py
src/stegcore/three_layer.py
tests/test_decision.py
tests/test_three_layer.py
docs/DECISION_MODEL.md
docs/POLICY_SHAPES.md
docs/CONTINUITY_ADMISSIBILITY_RECEIPT_MAPPING.md
docs/THREE_LAYER_ADMISSIBILITY_RUNTIME.md
scripts/check_continuity_admissibility_mapping.py
.github/workflows/runtime-tests.yml
```

## Three-Layer Runtime Contract

The Governance source contract is preserved in `StegVerse-Labs/Governance` and linked through issue #22.

StegCore implements three deterministic layers:

1. judgment conditions;
2. signal admission and reference-state formation integrity;
3. commit-time execution admissibility.

The runtime produces uppercase execution results:

```text
ALLOW
DENY
FAIL-CLOSED
```

These are distinct from lowercase Governance Decision Record values.

## Implemented Behavior

### Judgment conditions

The runtime denies when:

- meaningful refusal is unavailable;
- operator recoverability is degraded, unavailable, or unknown;
- declared overload or critical time pressure materially degrades judgment.

### Signal admission and state formation

The runtime denies when:

- no canonical signals are admitted;
- material inputs are missing;
- uncertainty is material or unknown;
- the admitted signal set cannot be reconstructed;
- transformation provenance is incomplete.

The runtime fails closed when:

- reference-state hashes are absent;
- the current reference-state hash differs from the expected authorized hash.

### Execution boundary

The runtime denies when:

- actor authority is stale;
- policy or delegation is stale;
- evidence is stale;
- the validity window is closed;
- affected-entity conditions are not represented.

The runtime fails closed when execution recoverability is unknown.

The runtime allows only when every required condition passes.

## Result and Receipt Shape

The result preserves:

- decision and reason code;
- layer-specific findings;
- canonical request hash;
- policy and delegation references;
- judgment evidence references;
- admitted signal references;
- execution evidence references;
- current and expected reference-state hashes;
- deterministic receipt hash;
- explicit `continuity_receipt_minted: false`.

## Automated Tests

`tests/test_three_layer.py` proves:

1. condition-degraded judgment yields `DENY`;
2. unreconstructable signal admission yields `DENY`;
3. governance validation of a shifted state yields `FAIL-CLOSED` even when policy and authority pass;
4. a complete positive control yields `ALLOW`;
5. replay with a changed reference state changes the result;
6. an unreconstructable state never yields `ALLOW`.

The existing decision tests remain part of the same automated suite.

## Validation Automation

`.github/workflows/runtime-tests.yml` runs automatically on relevant pushes and pull requests.

It:

1. installs StegCore and pytest;
2. validates the Continuity admissibility mapping;
3. runs the complete pytest suite.

Manual workflow dispatch remains only as an optional recovery path and is not required to initiate validation.

## Active Ownership

- Governance policy, schema mapping, and source fixtures: `StegVerse-Labs/Governance`.
- Runtime evaluator, result/receipt behavior, and automated tests: `StegVerse-Labs/StegCore`.
- Runtime implementation task: issue #22.
- Continuity receipt verification or minting: outside StegCore authority.
- Production deployment authority: not granted by this implementation.

## Manual Tasks Eliminated

- Runtime acceptance criteria are executable tests rather than manual review instructions.
- Validation starts on relevant pushes and pull requests.
- Continuity mapping validation is included in the same workflow.
- Replay behavior is tested automatically.
- Receipt non-minting is asserted in code and tests.
- Runtime placement is assigned and no longer requires a human choice.

## Remaining Work

1. Observe the automatic workflow result for the current commit chain.
2. Correct any automation failure through repository commits rather than manual workflow execution.
3. Record the passing run evidence in this handoff and issue #22.
4. Align Governance positive/replay fixtures with the final StegCore result object if field-level differences remain.
5. Close issue #22 only after automated validation passes.
6. Apply release/tagging rules only after repository release readiness is independently verified.
7. On release readiness, create or update verification tasks for `StegVerse-Labs/Site`, `GCAT-BCAT-Engine/Publisher`, `StegVerse-Labs/admissibility-wiki`, and `StegVerse-Labs/stegguardian-wiki`.

## Definition of Done

Runtime implementation is complete when:

- `src/stegcore/three_layer.py` remains aligned with the Governance contract;
- automated tests prove all required DENY, FAIL-CLOSED, ALLOW, and replay behaviors;
- automated validation passes;
- result receipts preserve all three layers and do not mint Continuity receipts;
- issue #22 and this handoff contain the passing evidence;
- future continuation requires no chat context or manual-only action.

## Current Completion Assessment

```text
Runtime contract: implemented
Negative acceptance behavior: implemented
Positive control: implemented
Replay test: implemented
Receipt shape: implemented
Automated validation workflow: implemented
Passing workflow evidence: pending observation
Production deployment authority: not claimed
Manual validation dependency: none
```

## Archive Readiness

```text
thread_archive_ready: true
archive_reason: all implementation decisions, code paths, tests, automation, authority boundaries, remaining work, and completion events are repository-resident.
```

## Progress Snapshot

```text
StegVerse-Labs - 88% complete
StegCore - 84% complete
StegCore - 96% complete TO GOAL ACTIVATION
Fully developed files vs scaffolding and stubs: 84% developed / 16% pending validation evidence and future deployment surfaces
Delta: the three-layer runtime, receipt contract, tests, and push-driven validation now exist; only automated run evidence, final cross-repo fixture alignment, and release-readiness evaluation remain.
```
