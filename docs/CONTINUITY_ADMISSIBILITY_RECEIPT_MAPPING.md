# Continuity Admissibility Receipt Mapping

## Purpose

This document maps StegVerse-Labs/Continuity continuation receipts to StegCore admissibility language.

It exists so a future session, workflow, or ecosystem worker can determine whether a continuation handoff has enough standing to proceed without relying on chat memory.

## Boundary

StegCore does not mint continuity receipts.

StegCore performs admissibility evaluation; it has no receipt-minting authority and does not acquire production authority from a Continuity receipt.

StegCore answers whether a proposed action is admissible at the time of action.

Continuity records the handoff, receipt, schema, examples, and reconstructability or recreatability basis.

The boundary is:

```text
Continuity receipt
  -> standing evidence
  -> StegCore admissibility check
  -> proceed, pause, or deny
```

## Required Continuation Receipt Fields

A continuation receipt must preserve:

```text
receipt_id
created_utc
source_repository
source_handoff_path
target_repository
target_handoff_path
current_goal
activation_state
standing_basis
files_built
files_pending
completion_assessment
next_integration_candidate
thread_archive_ready
```

## Admissibility Mapping

| Receipt field | StegCore interpretation | Required state |
|---|---|---|
| receipt_id | Stable reference for reconstruction | Present and unique within context |
| created_utc | Temporal boundary for review | Present |
| source_repository | Origin of continuation standing | Present |
| source_handoff_path | Source handoff artifact | Present and repository-local |
| target_repository | Repository receiving the task | Present |
| target_handoff_path | Target continuation artifact | Present or explicitly pending |
| current_goal | Claimed action scope | Present and bounded |
| activation_state | Current authority posture | Must not overclaim completion |
| standing_basis | Why the task may proceed | Present and specific |
| files_built | Evidence of completed work | Present |
| files_pending | Remaining work boundary | Present |
| completion_assessment | Build vs activation assessment | Present |
| next_integration_candidate | Next repository or module | Present or null with reason |
| thread_archive_ready | Whether chat context is still required | Explicit boolean |

## Proceed Conditions

StegCore should treat a continuation action as admissible when:

1. The source repository and target repository are explicit.
2. The source handoff path is repository-local.
3. The current goal is bounded.
4. The activation state does not overclaim completion.
5. The files built and pending are both listed.
6. The completion assessment separates built state from activation state.
7. The next integration candidate is explicit, or null with a clear reason.
8. The thread archive readiness value is explicit.
9. Any recreation-gate evidence required by the target transition is independently validated.

## Pause Conditions

StegCore should pause continuation when:

1. The target handoff path does not exist yet.
2. The current goal conflicts with the target repository mission.
3. The receipt claims activation but lists unresolved activation blockers.
4. The standing basis is generic or unverifiable.
5. Files are claimed as built but are not present in repository artifacts.
6. The continuation requires secrets, credentials, or manual action not represented in the repo.
7. Recreation, recovery, divergence, exposure, or verification-margin evidence is required but incomplete.

## Deny Conditions

StegCore should deny continuation when:

1. The receipt attempts to grant production authority by itself.
2. The receipt bypasses a repository-local handoff.
3. The receipt treats chat memory as the sole source of truth.
4. The receipt hides pending work while claiming completion.
5. The receipt crosses repository boundaries without naming source and target.
6. The action would overwrite established source-of-truth boundaries.
7. External AI output is treated as authoritative merely because it returned to a governed node.
8. Trusted and recreated state hashes differ without an admissible successor transition.

## Commit-Time Check

At commit time, StegCore should ask:

```text
Does the proposed repository action still match the receipt, handoff, current authority, current policy, unresolved conditions, and current repository state?
```

If the answer is no, the action should pause or deny rather than proceed.

## Mapping To Continuity Examples

The Continuity continuation receipt and `SV-CONTINUITY-109` recreation evidence are admissible only as evidence inputs until StegCore records a local decision receipt.

A Continuity receipt cannot self-authorize execution, replace StegCore evaluation, or confer receipt-minting authority.

## Current Status

```text
Resolved: Continuity receipt fields mapped to StegCore admissibility language.
Resolved: proceed, pause, and deny conditions defined.
Resolved: commit-time check defined.
Resolved: explicit production-authority and receipt-minting non-claims restored.
Resolved: recreation-gate evidence boundary incorporated.
Pending: repository-wide workflow confirmation.
```
