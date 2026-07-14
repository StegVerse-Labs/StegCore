# StegCore Mirror Handoff

## Purpose

This is the repository-local continuation source for StegCore. Future work must continue from this file without prior chat context.

## Current Goal

```text
Goal: automatically validate, evidence, reconcile failures, and advance the StegCore three-layer runtime to a governed release-readiness state
Repository: StegVerse-Labs/StegCore
Activation state: runtime_candidate_automated_reconciliation_active
Completion class: first_passing_evidence_pending
Manual action requirement: none_for_validation_evidence_failure_detection_issue_closure_or_readiness_initiation
Source of truth: runtime code, tests, workflows, canonical Governance fixtures, evidence records, issues, and this handoff
```

## Confirmed Repository Boundary

StegCore decides whether actions are permitted given already-resolved continuity, policy, authority, evidence, and state-integrity facts.

StegCore does not verify or mint Continuity receipts, store identity, replace StegID, create execution authority, or claim release, tagging, production, or deployment authority merely by producing a result or readiness assessment.

## Built Runtime and Automation Surfaces

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
scripts/record_runtime_validation.py
scripts/check_runtime_validation_evidence.py
scripts/assess_release_readiness.py
.github/workflows/runtime-tests.yml
```

## Three-Layer Contract

StegCore evaluates, in restrictive order:

1. judgment conditions;
2. signal admission and state-formation integrity;
3. commit-time execution admissibility.

Runtime outcomes are `ALLOW`, `DENY`, or `FAIL-CLOSED`. They remain distinct from lowercase Governance Decision Record values.

The runtime receipt preserves the decision, reason code, layer findings, canonical request hash, policy and delegation references, evidence references, admitted signals, current and expected reference-state hashes, receipt hash, and `continuity_receipt_minted: false`.

## Canonical Governance Fixture Set

StegCore evaluates six live fixtures from `StegVerse-Labs/Governance`:

```text
condition_degraded_judgment_gdr.json
signal_admission_drift_gdr.json
governance_validation_of_drift_gdr.json
three_layer_positive_control_gdr.json
three_layer_replay_baseline_gdr.json
three_layer_replay_mutated_gdr.json
```

The replay pair keeps policy, actor authority, and delegation constant while changing admitted signals and the reference-state hash. The required outcome changes from `ALLOW` to `FAIL-CLOSED`.

## Validation, Evidence, and Reconciliation Automation

`github/workflows/runtime-tests.yml`—shown without the leading dot for readability—runs automatically on relevant pushes, pull requests, a daily schedule, and optional recovery dispatch.

The workflow:

1. installs StegCore and pytest;
2. validates the Continuity admissibility mapping;
3. runs the full runtime test suite;
4. clones canonical Governance;
5. evaluates all six Governance fixtures through StegCore;
6. creates or refreshes `evidence/runtime-validation.json` after a passing non-PR run;
7. validates the evidence hash, required results, downstream destinations, and authority boundaries;
8. creates or refreshes `evidence/release-readiness.json`;
9. commits changed evidence to `main`;
10. closes implementation issue #22 after all gates pass;
11. closes any open automated failure issue after recovery;
12. creates or refreshes a release-readiness issue;
13. creates or refreshes an automated failure issue when validation fails.

Workflow concurrency serializes evidence writers. Evidence generation is idempotent for unchanged StegCore and Governance contract commits.

## Durable Evidence Records

Expected paths:

```text
evidence/runtime-validation.json
evidence/release-readiness.json
```

`runtime-validation.json` records the validated StegCore and Governance commits, run identity, test and contract results, receipt non-minting, downstream verification destinations, authority non-claims, and canonical evidence hash.

`release-readiness.json` records:

- state: `validated_not_released`;
- runtime, Continuity mapping, Governance contract, and evidence-integrity gates as passed;
- independent release policy as pending;
- downstream verification as pending;
- release and tagging as not permitted;
- the exact completion event required to change that state.

Neither record grants release or execution authority.

## Issue State Machine

### Implementation issue

- Issue #22 owns runtime implementation until every automated validation gate passes.
- A passing run closes it automatically with the validated commit references.

### Failure issue

- Title: `[automation] StegCore runtime validation failure`.
- A failed non-PR run creates or refreshes it with the failing commit and workflow URL.
- A later passing run closes it automatically.

### Release-readiness issue

- Title: `[release-readiness] StegCore three-layer candidate`.
- A passing run creates or refreshes it from the durable evidence records.
- It remains a coordination task and does not grant release authority.

## Active Ownership

- Governance policy, schema mapping, canonical fixtures, and fixture validation: `StegVerse-Labs/Governance`.
- Runtime evaluator, receipt behavior, cross-repository verifier, validation evidence, failure reconciliation, implementation closure, and readiness initiation: `StegVerse-Labs/StegCore`.
- Continuity receipt verification or minting: outside StegCore authority.
- Release and production authority: not granted by this workstream.

## Manual Tasks Eliminated

- Acceptance criteria are executable tests.
- Validation starts automatically.
- Canonical Governance fixtures are evaluated live.
- Scheduled verification detects later drift.
- Passing evidence is generated, validated, and committed automatically.
- Evidence publication is idempotent and concurrency-safe.
- Issue #22 closes automatically only after all gates pass.
- Failed runs create a durable repair issue automatically.
- Recovery closes the repair issue automatically.
- Passing evidence initiates and refreshes the release-readiness task automatically.
- Release remains blocked by machine-readable pending gates rather than informal judgment.
- Manual dispatch remains only as an optional recovery route.

## Remaining Work

1. Allow the first successful non-PR validation run to create both evidence records, close issue #22, and create the release-readiness issue.
2. Correct any validation failure through repository commits; the workflow owns failure notification and recovery reconciliation.
3. Satisfy an independent release policy before permitting a tag.
4. Durably complete the four downstream verification gates:
   - `StegVerse-Labs/Site`;
   - `GCAT-BCAT-Engine/Publisher`;
   - `StegVerse-Labs/admissibility-wiki`;
   - `StegVerse-Labs/stegguardian-wiki`.
5. Change release or tag permission only through a governed update to the machine-readable readiness record and its validator.

## Definition of Done

Runtime activation is complete when:

- unit tests pass;
- the Continuity mapping validator passes;
- the live Governance fixture contract passes;
- receipts preserve all three layers and do not mint Continuity receipts;
- `evidence/runtime-validation.json` exists with `status: pass`;
- `evidence/release-readiness.json` exists with `state: validated_not_released`;
- issue #22 is closed by automation;
- failure reconciliation operates without manual monitoring;
- release authority remains bounded by the independent release and downstream gates;
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
Idempotent validation evidence: implemented
Evidence integrity validator: implemented
Deterministic release-readiness assessment: implemented
Automatic implementation closure: implemented
Automatic failure reconciliation: implemented
Automatic readiness issue initiation: implemented
Passing evidence records: pending first successful non-PR run
Release permission: blocked by independent policy and downstream gates
Manual activation dependency: none
```

## Archive Status

```text
thread_archive_ready: true
archive_reason: all implementation, validation, evidence, failure, closure, readiness, authority, ownership, and continuation mechanics are repository-resident.
```

## Progress Snapshot

```text
StegVerse-Labs - 95% complete
StegCore - 98% complete
StegCore - 99% complete TO GOAL ACTIVATION
Fully developed files vs scaffolding and stubs: 98% developed / 2% pending first passing evidence and governed release gates
Delta: validation success, validation failure, implementation closure, and readiness initiation are now automated state transitions; only the external run outcome and independently governed downstream release gates remain.
```
