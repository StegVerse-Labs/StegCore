# StegVerse Ecosystem Management Mirror Handoff

## Target repo

```text
StegVerse-Labs/StegCore
```

## Purpose

This is the ecosystem-level mirror handoff for autonomous task handoff and completion assessment.

## Admissible-Existence conformance gate

Every recently completed, current, and future worker task must be checked against the current StegCore Admissible-Existence lifecycle before this handoff or the worker registry may treat the task as conformant continuation state.

Canonical surfaces:

```text
ecosystem_management/ae_task_conformance.v1.json
ecosystem_management/task_registry.yml
management/admissible-existence-capability-registry.json
tools/verify_ae_handoff_task_conformance.py
brain_reports/ae_handoff_task_conformance_report.json
```

Required procedure:

```text
1. Resolve the worker task identity and temporal class: recently completed, current, or future.
2. Resolve its AE relationship: develops_capability, integrates_capability, validates_capability, or propagates_capability.
3. Bind it to exactly one canonical capability existence unless a separately governed multi-capability manifest explicitly applies.
4. Verify the capability declaration hash and current registry phase.
5. Verify the handoff and worker-task projections agree on task owner, capability binding, claimed phase, blockers, and continuation owner.
6. For recently completed work, require retained evidence sufficient for the claimed phase; file/PR presence is not completion evidence by itself.
7. For current work, require an owner, continuation owner, explicit blockers, and a phase claim that does not exceed the capability registry.
8. For future work, require a capability binding and target phase before activation work can begin. A future task cannot self-claim activation.
9. ACTIVATED requires standing + admissibility + integration evidence and an explicit activation proof with no unresolved activation blockers.
10. ADMISSIBLE with blockers requires a durable continuation owner.
11. Legacy task records without AE binding are MIGRATION_REQUIRED and cannot silently carry authority forward or activate a successor task.
12. Run `python tools/verify_ae_handoff_task_conformance.py`; only PASS may be treated as canonical conformance.
```

Canonical StegGate remains `stegcore.steggate.evaluate_admissibility`. This verification layer is structural only: it may block a task/handoff lifecycle claim but may not widen a canonical disposition, execute a capability, mint a continuity receipt, grant release authority, or reinterpret TV/TVC credential authority. GitHub token runtime authority remains NONE.

The first retrospective post-AE check is transaction discovery (#83/#98/#103): source/storage development is registered as ADMISSIBLE, with consumer/public discovery binding still blocking ACTIVATED.

## New goal

Continue ecosystem building until either:

```text
1. The active task chain is complete; or
2. The ecosystem can determine, hand off, verify, and close the next task using its own management receipts.
```

## Management rule

A repo is management-capable when it exposes:

```text
MIRROR_HANDOFF.md or equivalent repo handoff
machine-readable task registry entry
completion criteria
next integration candidate
verification command
receipt/report artifact
non-overlap statement for parallel sessions
archive readiness statement
Admissible-Existence capability/task binding
AE conformance verification result
```

## Current StegFin provider chain

```text
stegfin-governance
StegCore StegFin intake
TVC executor intake
stegfin-executor
stegfin-adapter
stegfin-provider-token-ledger
stegfin-provider-token-ledger-executor
stegfin-provider-token-ledger-executor/live_execution shadow
stegfin-provider-treasury-record
stegfin-provider-banking
```

## Current next candidate

```text
StegVerse-Labs/stegfin-provider-acquisition-close
```

## Boundary

Ecosystem management may select, hand off, and verify tasks. It does not silently grant execution authority to financial, legal, banking, token, or deployment actions.
