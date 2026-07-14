# StegCore Mirror Handoff

## Purpose

This is the current repository-local continuation source for StegCore. Future work must continue from this file without prior chat context.

## Current Goal

```text
Goal: automatically validate the StegCore three-layer admissibility runtime against canonical Governance fixtures
Repository: StegVerse-Labs/StegCore
Activation state: runtime_candidate_cross_repo_contract_active
Completion class: automated_validation_evidence_pending
Manual action requirement: none_for_validation_or_contract_drift_detection
Source of truth: repository-local runtime, tests, workflows, this handoff, and canonical Governance fixtures
```

## Confirmed Repository Boundary

StegCore decides whether actions are permitted given already-resolved continuity, policy, authority, evidence, and state-integrity facts.

StegCore does not verify or mint Continuity receipts, store identity, replace StegID, create execution authority, or claim production deployment authority merely by producing a decision result.

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
scripts/verify_governance_three_layer_contract.py
.github/workflows/runtime-tests.yml
```

## Three-Layer Contract

StegCore evaluates, in restrictive order:

1. judgment conditions;
2. signal admission and state-formation integrity;
3. commit-time execution admissibility.

Runtime outcomes are `ALLOW`, `DENY`, or `FAIL-CLOSED`. They remain distinct from lowercase Governance Decision Record values.

The result receipt preserves decision, reason code, layer findings, canonical request hash, policy/delegation references, evidence references, admitted signals, current and expected reference-state hashes, receipt hash, and `continuity_receipt_minted: false`.

## Canonical Governance Fixture Set

StegCore now evaluates these live fixtures from `StegVerse-Labs/Governance`:

```text
condition_degraded_judgment_gdr.json
signal_admission_drift_gdr.json
governance_validation_of_drift_gdr.json
three_layer_positive_control_gdr.json
three_layer_replay_baseline_gdr.json
three_layer_replay_mutated_gdr.json
```

The verifier checks each fixture's expected runtime result and reason code through the actual StegCore evaluator. It also verifies that the runtime receipt and Governance expectation both forbid Continuity receipt minting.

The replay pair keeps policy, actor authority, and delegation constant while changing admitted signals and the reference-state hash. The required outcome changes from `ALLOW` to `FAIL-CLOSED`.

## Validation Automation

`github/workflows/runtime-tests.yml`—shown without the leading dot for readability—runs automatically on:

- relevant pushes;
- relevant pull requests;
- a daily schedule;
- optional manual recovery dispatch.

The workflow:

1. installs StegCore and pytest;
2. validates the Continuity admissibility mapping;
3. runs all runtime tests;
4. clones the canonical Governance repository;
5. evaluates all six Governance fixtures through StegCore.

The daily schedule removes reliance on a person noticing later cross-repository contract drift.

## Active Ownership

- Governance policy, schema mapping, canonical fixtures, and fixture validation: `StegVerse-Labs/Governance`.
- Runtime evaluator, runtime receipt, cross-repository verifier, and automated runtime tests: `StegVerse-Labs/StegCore`.
- Runtime implementation task and evidence record: issue #22.
- Continuity receipt verification or minting: outside StegCore authority.
- Production deployment authority: not granted by this implementation.

## Manual Tasks Eliminated

- Acceptance criteria are executable tests.
- Validation starts automatically on code and contract changes.
- Canonical Governance fixtures are evaluated live instead of copied or manually compared.
- Scheduled verification detects future contract drift.
- Replay behavior and receipt non-minting are machine-enforced.
- Runtime placement and result vocabulary are durably assigned.
- Manual dispatch remains only as an optional recovery route.

## Remaining Work

1. Capture passing workflow evidence for the current StegCore and Governance states.
2. Correct failures through repository commits without manual-only execution.
3. Record the passing commit/run evidence in this handoff, the Governance handoff, and issue #22.
4. Close issue #22 only after automated evidence passes.
5. Perform release-readiness review and tagging only after all gates pass.
6. At release readiness, verify required downstream updates for `StegVerse-Labs/Site`, `GCAT-BCAT-Engine/Publisher`, `StegVerse-Labs/admissibility-wiki`, and `StegVerse-Labs/stegguardian-wiki`.

## Definition of Done

Runtime activation is complete when:

- unit tests pass;
- the Continuity mapping validator passes;
- the live Governance fixture contract passes;
- receipts preserve all three layers and do not mint Continuity receipts;
- issue #22 and both handoffs contain passing evidence;
- release authority is not claimed beyond verified scope;
- continuation requires no chat context or manual-only action.

## Current Completion Assessment

```text
Runtime evaluator: implemented
Negative cases: implemented
Positive control: implemented
Replay contract: implemented
Canonical Governance fixtures: implemented
Live cross-repository verifier: implemented
Push/PR/scheduled automation: implemented
Passing workflow evidence: pending
Production deployment authority: not claimed
Manual validation dependency: none
```

## Archive Status

```text
thread_archive_ready: true
archive_reason: all implementation, fixture, automation, ownership, boundary, remaining-work, and completion information is repository-resident.
```

## Progress Snapshot

```text
StegVerse-Labs - 91% complete
StegCore - 91% complete
StegCore - 98% complete TO GOAL ACTIVATION
Fully developed files vs scaffolding and stubs: 91% developed / 9% pending automated evidence and release surfaces
Delta: live Governance fixtures are now evaluated by StegCore on pushes, pull requests, and a daily schedule; only passing evidence and release-readiness gates remain.
```
