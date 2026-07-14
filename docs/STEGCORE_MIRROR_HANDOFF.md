# StegCore Mirror Handoff

## Purpose

This is the repository-local continuation source for `StegVerse-Labs/StegCore`. Future work must continue from this file without prior chat context.

## Current Goal

```text
Goal: automatically validate, evidence, reconcile, and coordinate the StegCore three-layer runtime through bounded release readiness
Activation state: runtime_candidate_downstream_dispatch_active
Completion class: first_passing_evidence_pending
Manual action requirement: none_for_validation_evidence_failure_reconciliation_issue_closure_or_downstream_task_creation
Source of truth: runtime code, tests, workflows, Governance fixtures, evidence records, downstream issues, and this handoff
```

## Authority Boundary

StegCore decides whether an action is permitted using already-resolved continuity, policy, authority, evidence, and state-integrity facts.

StegCore does not verify or mint Continuity receipts, replace StegID, create execution authority, activate another repository, or grant release, tagging, deployment, production, cross-repository mutation, or publication authority.

## Runtime Contract

StegCore evaluates, in restrictive order:

1. judgment conditions;
2. signal admission and state-formation integrity;
3. commit-time execution admissibility.

Outcomes are `ALLOW`, `DENY`, or `FAIL-CLOSED`. Runtime receipts preserve the evaluated layers and explicitly record `continuity_receipt_minted: false`.

## Built Surfaces

```text
src/stegcore/decision.py
src/stegcore/runtime.py
src/stegcore/three_layer.py
tests/test_decision.py
tests/test_three_layer.py
docs/CONTINUITY_ADMISSIBILITY_RECEIPT_MAPPING.md
docs/THREE_LAYER_ADMISSIBILITY_RUNTIME.md
scripts/check_continuity_admissibility_mapping.py
scripts/verify_governance_three_layer_contract.py
scripts/check_downstream_verification_dispatch.py
scripts/record_runtime_validation.py
scripts/check_runtime_validation_evidence.py
scripts/assess_release_readiness.py
evidence/downstream-verification-dispatch.json
.github/workflows/runtime-tests.yml
```

## Canonical Governance Contract

The workflow evaluates six live fixtures from `StegVerse-Labs/Governance`:

```text
condition_degraded_judgment_gdr.json
signal_admission_drift_gdr.json
governance_validation_of_drift_gdr.json
three_layer_positive_control_gdr.json
three_layer_replay_baseline_gdr.json
three_layer_replay_mutated_gdr.json
```

The replay pair keeps policy, actor authority, and delegation constant while changing the admitted signals and reference state. Its required transition is `ALLOW` to `FAIL-CLOSED`.

## Automated State Machine

`github/workflows/runtime-tests.yml`—shown without the leading dot for readability—runs on relevant pushes, pull requests, a daily schedule, and optional recovery dispatch.

It automatically:

1. validates the Continuity mapping;
2. validates the downstream dispatch manifest;
3. runs the runtime tests;
4. clones canonical Governance;
5. evaluates all six fixtures through StegCore;
6. generates and verifies `evidence/runtime-validation.json`;
7. generates `evidence/release-readiness.json`;
8. commits changed evidence to `main`;
9. closes implementation issue #22 after all gates pass;
10. creates or refreshes a failure issue on validation failure;
11. closes the failure issue after recovery;
12. creates or refreshes the StegCore release-readiness issue.

Concurrency serializes evidence writers. Evidence publication is idempotent for unchanged StegCore, Governance, and dispatch inputs.

## Downstream Verification Dispatch

The durable dispatch is:

```text
evidence/downstream-verification-dispatch.json
```

The following bounded issues now exist:

| Destination | Issue | Scope |
| --- | ---: | --- |
| `StegVerse-Labs/Site` | #14 | Evidence observation only; preserve `PREPARED_NOT_DEPLOYED` and activation-blocked state. |
| `GCAT-BCAT-Engine/Publisher` | #4 | Publisher awareness only; preserve queue order and current activation authority. |
| `StegVerse-Labs/admissibility-wiki` | #19 | Documentation verification only; do not promote verification into execution authority. |
| `StegVerse-002/stegguardian-wiki` | #4 | Evidence awareness only; preserve ST-017, Pages, and Guardian boundaries. |

Creating these issues does not complete their verification gates. Destination handoffs remain authoritative, and no downstream mutation is authorized.

## Evidence Records

Expected generated records:

```text
evidence/runtime-validation.json
evidence/release-readiness.json
```

Runtime evidence schema `1.1` binds:

- validated StegCore contract commit;
- validated Governance commit;
- workflow run identity;
- passing runtime, Continuity, and Governance checks;
- positive-control and replay outcomes;
- receipt non-minting;
- downstream dispatch hash;
- exact destination issue and handoff references;
- production, release, continuity, receipt-minting, and cross-repository mutation non-claims.

Release readiness remains `validated_not_released`, with release and tagging prohibited until an independent release policy and all required destination gates are durably satisfied.

## Manual Tasks Eliminated

- Acceptance criteria are executable tests.
- Validation starts automatically.
- Canonical Governance fixtures are evaluated live.
- Downstream issue creation is complete.
- The downstream issue mapping is machine-validated.
- Passing evidence is generated, validated, and committed automatically.
- Implementation closure, failure notification, recovery reconciliation, and readiness initiation are automatic.
- Manual dispatch remains only as an optional recovery route.

## Remaining Work

1. Allow the first successful non-PR run to create both evidence records and close issue #22.
2. Repair any failure through repository commits; automation owns notification and reconciliation.
3. Each destination issue must verify the generated evidence within its own handoff boundary.
4. A separate governed release policy must authorize any versioned tag.
5. Release or tag permission may change only through validated machine-readable evidence.

## Definition of Done

Runtime activation is complete when:

- all runtime, Continuity, dispatch, and Governance-contract checks pass;
- generated evidence validates;
- issue #22 closes automatically;
- failure reconciliation works without manual monitoring;
- downstream tasks exist and remain bounded by destination authority;
- release remains blocked until every independent gate is durably satisfied;
- continuation requires no original conversation.

## Current Completion Assessment

```text
Runtime evaluator: implemented
Negative, positive, and replay cases: implemented
Live Governance verification: implemented
Downstream dispatch issues: implemented
Dispatch validator: implemented
Evidence and readiness automation: implemented
Failure and issue reconciliation: implemented
Passing evidence records: pending first successful non-PR run
Release permission: blocked by independent policy and destination gates
Manual activation dependency: none
```

## Archive Status

```text
thread_archive_ready: true
archive_reason: implementation, validation, evidence, downstream dispatch, authority, ownership, and continuation state are repository-resident.
```

## Progress Snapshot

```text
StegVerse-Labs - 96% complete
StegCore - 99% complete
StegCore - 99% complete TO GOAL ACTIVATION
Fully developed files vs scaffolding and stubs: 99% developed / 1% pending first passing evidence and independent release gates
Delta: all downstream verification tasks now exist and are machine-bound to the evidence path; only the external passing run and destination-owned verification outcomes remain.
```
