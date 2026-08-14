# AE Handoff + Worker Task Conformance Mirror Handoff

## Canonical goal

```text
goal_id: AE-HANDOFF-TASK-CONFORMANCE-001
issue: StegVerse-Labs/StegCore#106
repository: StegVerse-Labs/StegCore
branch: feat/ae-handoff-task-conformance-001
role: canonical structural conformance verification
credential_authority: TV/TVC
github_token_runtime_authority: NONE
```

## Purpose

Prevent a handoff, worker task registry entry, completed-task claim, current-task claim, or future task from drifting behind the current StegCore Admissible-Existence design.

The handoff and worker task registry are projections of governed work state. Neither projection may independently enlarge capability phase or authority.

## Canonical surfaces

```text
ecosystem_management/ae_task_conformance.v1.json
management/admissible-existence-capability-registry.json
ecosystem_management/task_registry.yml
docs/STEGVERSE_ECOSYSTEM_MANAGEMENT_MIRROR_HANDOFF.md
tools/verify_ae_handoff_task_conformance.py
tests/test_ae_handoff_task_conformance.py
.github/workflows/verify-task-registry.yml
brain_reports/ae_handoff_task_conformance_report.json
```

## Verification classes

### Recently completed

A task may retain a completed classification only if its declared relationship to a capability is resolvable and retained evidence supports the claimed AE phase. Source existence, PR merge, or workflow existence alone may not imply ACTIVATED.

### Current

Current tasks require exact task identity, capability relationship, current capability phase, owner, continuation owner, blockers, handoff reference, and retained evidence. A current task cannot claim a phase above the canonical capability registry.

### Future

Future tasks require a capability binding and target phase before activation work begins. They may not self-claim activation. A future task derived from a legacy record without AE binding is fail-closed as `MIGRATION_REQUIRED`.

## Relationship model

Worker tasks do not automatically become capability-existence entries. Each task declares one relationship:

```text
develops_capability
integrates_capability
validates_capability
propagates_capability
```

A `develops_capability` task must bind to a canonical capability existence. Integration/validation/propagation tasks bind to an existing capability and cannot change its phase merely by completing their own task.

## Capability lifecycle requirements

Canonical phases:

```text
DECLARED
STANDING
ADMISSIBLE
ACTIVATED
SUSPENDED
SUPERSEDED
TERMINATED
```

Canonical admissibility runtime remains:

```text
stegcore.steggate.evaluate_admissibility
```

Structural verification may only block. It cannot convert DENY, REVIEW, or FAIL_CLOSED into ALLOW and cannot execute external consequences or mint continuity receipts.

`ACTIVATED` requires integration evidence and an explicit activation proof and may not retain unresolved activation blockers. `ADMISSIBLE` with blockers requires a durable continuation owner.

## Initial retrospective reconciliation

Transaction discovery is the first post-AE completed task reconciled through this procedure:

```text
capability_id: stegverse:capability:transaction-discovery:v1
source: StegCore #83 / worker-assist #98 / PR #103
phase: ADMISSIBLE
activation_claimed: false
blocker: CONSUMER_PUBLIC_DISCOVERY_BINDING_NOT_YET_PROVEN
continuation_owner: StegVerse-Labs/StegCore#83
```

This explicitly prevents the merged durable SQLite discovery provider from being misreported as a live consumer/public activation.

## Legacy migration rule

Pre-AE task registry chains are preserved but marked `MIGRATION_REQUIRED_UNTIL_BOUND_IN_AE_TASK_CONFORMANCE_MANIFEST`. Their historical evidence remains usable as evidence; their old classification does not silently carry activation authority forward.

## Canonical command

```bash
python tools/verify_ae_handoff_task_conformance.py
```

A PASS report is required before ecosystem-management readiness may report handoff capability. `tools/assess_ecosystem_management_readiness.py` is subordinate to this report.

## Workflow authority boundary

`.github/workflows/verify-task-registry.yml` uses empty repository permissions, explicit credential absence checks, anonymous source acquisition with credential suppression, system Python, and log-retained hashes. Hosted workflow execution is validation evidence only and has no runtime or capability authority.

## Completion condition

This goal is complete when:

1. the canonical manifest, verifier, tests, handoff procedure, worker-registry projection, and capability-registry retrospective entry are merged;
2. the canonical verifier passes against the exact merged state;
3. the ordinary capability-registry validator passes;
4. the ecosystem management readiness assessor consumes and requires the AE report;
5. issue #106 records exact validation and merge evidence.
