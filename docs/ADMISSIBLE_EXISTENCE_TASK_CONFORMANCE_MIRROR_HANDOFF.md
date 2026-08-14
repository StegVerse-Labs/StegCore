# Admissible-Existence Task Conformance Mirror Handoff

```text
organization: StegVerse-Labs
repository: StegCore
active_goal_id: ADMISSIBLE-EXISTENCE-TASK-CONFORMANCE-003
formalism_authority: Admissible-Existence/AE
canonical_runtime_authority: stegcore.steggate.evaluate_admissibility
credential_authority: TV/TVC
github_token_runtime_authority: NONE
archive_ready: false
```

## Purpose

This is the canonical continuation record for verification of HANDOFF and Worker Task Registry task-state claims against the StegCore Admissible-Existence structural lifecycle.

The verifier does not replace StegGate, execute tasks, infer activation, mint continuity receipts, or own credentials. It fail-closes continuation metadata when operational state claims are not backed by the AE phase and evidence required by the canonical policy.

## Canonical surfaces

Both surfaces are mandatory inputs to the same verification procedure:

1. HANDOFF conformance manifest;
2. Worker Task Registry.

The verifier covers three horizons in both surfaces:

- `recently_completed`;
- `current`;
- `future`.

A task cannot be omitted from verification merely because it is already merged, not yet started, blocked, or assigned to another worker.

## Canonical implementation

```text
management/admissible-existence-task-conformance-policy.json
management/admissible-existence-task-conformance-handoff.json
scripts/verify_admissible_existence_task_conformance.py
tests/test_admissible_existence_task_conformance.py
```

## Required task semantics

Each task must preserve two distinct state dimensions:

```text
operational state
  CLAIMED / ACTIVE / BLOCKED / RETRY / REVIEW_REQUIRED / FAILED / COMPLETE / SUPERSEDED / MERGED

Admissible-Existence phase
  DECLARED / STANDING / ADMISSIBLE / ACTIVATED / SUSPENDED / SUPERSEDED / TERMINATED
```

Operational completion is not activation. A source-complete or merged task may legitimately remain `ADMISSIBLE` when live activation evidence is absent. Any `ACTIVATED` claim requires an explicit activation proof reference.

## Evidence rules

The gate verifies:

- standing evidence for STANDING and later;
- admissibility evidence for ADMISSIBLE and later;
- explicit activation proof for ACTIVATED/SUSPENDED/SUPERSEDED lifecycle claims;
- blockers are absent from ACTIVATED entries;
- active work has a durable continuation owner;
- future tasks are not represented as terminal;
- credential authority remains `TV/TVC`;
- GitHub-token runtime authority remains false;
- completion is not inferred from file/branch/PR/workflow presence.

## Canonical procedure

```text
1. Recover newest StegCore AE policy and capability-registry state.
2. Enumerate recently completed, current, and future tasks from the HANDOFF.
3. Enumerate the same horizons from the Worker Task Registry.
4. Bind each task to an explicit AE phase.
5. Verify standing/admissibility/activation evidence required for that phase.
6. Verify collision boundary, continuation owner, and next executable action.
7. Verify TV/TVC credential authority and zero GitHub-token runtime authority.
8. Fail closed on missing evidence, invalid phase/state combinations, or false activation.
9. Emit a deterministic conformance receipt committing to policy, HANDOFF, and registry hashes.
10. Permit archival/activation claims only when the relevant task entries pass and stronger runtime evidence, where required, exists.
```

## Command

```bash
python scripts/verify_admissible_existence_task_conformance.py \
  --handoff management/admissible-existence-task-conformance-handoff.json \
  --registry /path/to/worker-task-registry.json \
  --receipt /tmp/admissible-existence-task-conformance.receipt.json
```

Exit `0` means the continuation surfaces conform structurally. Exit `1` means `FAIL_CLOSED`.

A PASS is not itself proof that work executed or a capability activated. It means the continuation surfaces accurately describe their current standing under the canonical AE policy.

## Current horizon inventory

### Recently completed

`ADMISSIBLE-EXISTENCE-CAPABILITY-MODEL-001` is preserved as completed with explicit evidence and a released collision boundary.

### Current

`ADMISSIBLE-EXISTENCE-TASK-CONFORMANCE-003` owns this verifier, policy, tests, and canonical binding procedure until hosted validation and merge are evidenced.

### Future

`ADMISSIBLE-EXISTENCE-CONSUMER-BINDING-004` is declared but cannot become terminal or activated until consumer repositories actually adopt the contract and produce evidence.

## Archive rule

A session or worker lane is not archive-ready merely because its task says COMPLETE or MERGED. The applicable HANDOFF and Worker Task Registry entries must pass this gate, retain any remaining continuation ownership, and must not overstate AE phase or activation.
