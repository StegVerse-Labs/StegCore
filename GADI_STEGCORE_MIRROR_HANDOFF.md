# GADI StegCore Mirror Handoff

Updated: 2026-09-07
Organization: `StegVerse-Labs`
Repository: `StegVerse-Labs/StegCore`
Branch: `gadi-stegcore-001`
Task ID: `GADI-STEGCORE-001`
Parent task: `GADI-001`
Umbrella task: `GOVERNED-MULTILANE-MANIFOLD-ACTIVATION-001`
COSV ID: `10100000100000`
Canonical issue: `StegVerse-Labs/StegCore#190`
Status: `IMPLEMENTATION CLAIMED IN SESSION / SOURCE BUILD IN PROGRESS / RUNTIME ACTIVATION NOT CLAIMED`

## Source of truth

This file is the repo-local continuation record for the StegCore GADI reasoning/planning slice required by `StegVerse-Labs/StegCore#190`.

Inherited authority and contracts:
- `MANIFOLD_GOVERNANCE_MIRROR_HANDOFF.md`
- `StegVerse-Labs/.github/docs/GOVERNED_MULTILANE_MANIFOLD_ACTIVATION_MIRROR_HANDOFF.md`
- `StegVerse-Labs/.github/docs/GADI_MIRROR_HANDOFF.md`
- `StegVerse-Labs/StegOS/docs/GADI_STEGOS_MIRROR_HANDOFF.md`
- `StegVerse-Labs/StegOS/stegos/gadi_contracts.py`

Canonical runtime governance remains StegCore/StegGate/InTr. Credential authority remains TV/TVC. Wallet signing/broadcast remains USER_ONLY.

## Objective

Implement the non-authorizing StegCore slice that consumes validated autonomous threat observations, correlates them into governed threat state while preserving provenance and uncertainty, generates competing defensive intervention candidates, deterministically selects the least-destructive effective candidate, and emits a `stegos.defensive_intervention_request.v1` payload that still requires existing InTr/StegGate admission before actuation.

## Authority boundary

This task may not:
- admit or execute an intervention itself;
- mint credentials or runtime authority;
- create a second StegGate evaluator, worker registry, heartbeat, scheduler, claim/fence mechanism, or runtime-truth source;
- convert model output, confidence, urgency, or threat severity into authorization;
- target unauthorized third-party systems.

The output is planning evidence only until admitted by existing governance authority and bound to a pre-authorized defensive capability.

## Planned developed files

- `src/stegcore/gadi_defense_planner.py`
- `tests/test_gadi_defense_planner.py`
- `GADI_STEGCORE_MIRROR_HANDOFF.md`

## Acceptance tests

Coverage must include:
- positive credible-threat path;
- ambiguous/material-uncertainty path;
- stale observation fail-closed path;
- over-scoped capability fail-closed path;
- non-admitted output remaining non-authorizing;
- deterministic least-destructive candidate selection;
- provenance and uncertainty retention.

## Completion boundary

Source completion for `GADI-STEGCORE-001` requires the implementation and tests above to pass and the branch to be validated/merged through the repository's existing controls. It does not prove GADI runtime activation and does not satisfy the parent manifold activation by itself.

After merge, upstream `.github` must re-observe the child disposition and continue canonical WorkerCoordinator/resident traversal. Any release/tag decision remains blocked until owning-repository release criteria are met.
