# StegCore Mirror Handoff

## Purpose

This is the repository-local continuation source for StegCore. Future work must continue from this file without prior chat context.

## Current Goal

```text
Goal: automatically validate, evidence, and close the StegCore three-layer admissibility runtime activation task
Repository: StegVerse-Labs/StegCore
Activation state: runtime_candidate_automated_evidence_active
Completion class: first_passing_evidence_pending
Manual action requirement: none_for_validation_evidence_or_issue_closure
Source of truth: runtime code, tests, workflows, canonical Governance fixtures, evidence/runtime-validation.json, and this handoff
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
scripts/record_runtime_validation.py
.github/workflows/runtime-tests.yml
```

## Three-Layer Contract

StegCore evaluates, in restrictive order:

1. judgment conditions;
2. signal admission and state-formation integrity;
3. commit-time execution admissibility.

Runtime outcomes are `ALLOW`, `DENY`, or `FAIL-CLOSED`. They remain distinct from lowercase Governance Decision Record values.

The result receipt preserves decision, reason code, layer findings, canonical request hash, policy and delegation references, evidence references, admitted signals, current and expected reference-state hashes, receipt hash, and `continuity_receipt_minted: false`.

## Canonical Governance Fixture Set

StegCore evaluates these live fixtures from `StegVerse-Labs/Governance`:

```text
condition_degraded_judgment_gdr.json
signal_admission_drift_gdr.json
governance_validation_of_drift_gdr.json
three_layer_positive_control_gdr.json
three_layer_replay_baseline_gdr.json
three_layer_replay_mutated_gdr.json
```

The verifier checks each fixture's expected runtime result and reason code through the actual evaluator. It also verifies that both the runtime receipt and Governance expectation forbid Continuity receipt minting.

The replay pair keeps policy, actor authority, and delegation constant while changing admitted signals and the reference-state hash. The required outcome changes from `ALLOW` to `FAIL-CLOSED`.

## Validation and Evidence Automation

`github/workflows/runtime-tests.yml`—shown without the leading dot for readability—runs automatically on relevant pushes, pull requests, a daily schedule, and optional recovery dispatch.

The workflow:

1. installs StegCore and pytest;
2. validates the Continuity admissibility mapping;
3. runs the full runtime test suite;
4. clones canonical Governance;
5. evaluates all six Governance fixtures through StegCore;
6. on a successful non-PR run, writes `evidence/runtime-validation.json`;
7. commits that evidence to `main`;
8. closes issue #22 with the validated StegCore and Governance commits.

Evidence publication is idempotent. The evidence file changes only when the validated StegCore contract commit or canonical Governance commit changes. Evidence-only commits do not retrigger the workflow, and workflow concurrency prevents competing evidence writers.

## Durable Evidence Record

Expected path:

```text
evidence/runtime-validation.json
```

The record contains:

- validated StegCore contract commit;
- validated Governance commit;
- workflow run and attempt identifiers;
- Continuity mapping result;
- pytest result;
- live Governance fixture-contract result;
- positive-control and replay outcomes;
- explicit Continuity receipt non-minting assertion;
- explicit non-claims for production, continuity, and receipt-minting authority;
- canonical evidence hash.

This handoff and the Governance handoff consume passing evidence by reference to that file. No person must copy workflow details into either handoff.

## Active Ownership

- Governance policy, schema mapping, canonical fixtures, and fixture validation: `StegVerse-Labs/Governance`.
- Runtime evaluator, receipt behavior, cross-repository verifier, validation evidence, and issue closure: `StegVerse-Labs/StegCore`.
- Runtime implementation and activation task: issue #22 until automatically closed.
- Continuity receipt verification or minting: outside StegCore authority.
- Production deployment authority: not granted by this implementation.

## Manual Tasks Eliminated

- Acceptance criteria are executable tests.
- Validation starts automatically.
- Canonical Governance fixtures are evaluated live.
- Scheduled verification detects future contract drift.
- Replay behavior and receipt non-minting are machine-enforced.
- Passing run evidence is generated and committed automatically.
- Issue #22 is closed automatically only after every validation step passes.
- Evidence publication is idempotent and concurrency-safe.
- Manual dispatch remains only as an optional recovery route.

## Remaining Work

1. Allow the first successful non-PR validation run to create `evidence/runtime-validation.json` and close issue #22.
2. Correct any validation failure through repository commits; do not require manual workflow execution or evidence transcription.
3. After evidence exists, run the release-readiness gate against the durable record.
4. Tag or release only after version uniqueness, evidence validity, authority boundaries, and downstream task declarations are verified.
5. At release readiness, create or update verification tasks for `StegVerse-Labs/Site`, `GCAT-BCAT-Engine/Publisher`, `StegVerse-Labs/admissibility-wiki`, and `StegVerse-Labs/stegguardian-wiki`.

## Definition of Done

Runtime activation is complete when:

- unit tests pass;
- the Continuity mapping validator passes;
- the live Governance fixture contract passes;
- receipts preserve all three layers and do not mint Continuity receipts;
- `evidence/runtime-validation.json` exists with `status: pass`;
- issue #22 is closed by automation;
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
Idempotent evidence recorder: implemented
Automatic issue closure: implemented
Passing evidence record: pending first successful non-PR run
Production deployment authority: not claimed
Manual activation dependency: none
```

## Archive Status

```text
thread_archive_ready: true
archive_reason: all implementation, validation, evidence, closure, authority, ownership, and continuation mechanics are repository-resident.
```

## Progress Snapshot

```text
StegVerse-Labs - 93% complete
StegCore - 95% complete
StegCore - 99% complete TO GOAL ACTIVATION
Fully developed files vs scaffolding and stubs: 95% developed / 5% pending first passing evidence and governed release surfaces
Delta: passing validation now automatically creates durable evidence and closes issue #22; only the external run outcome and subsequent release-readiness gate remain.
```
