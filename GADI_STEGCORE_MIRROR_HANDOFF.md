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
Pull request: `StegVerse-Labs/StegCore#191`
Status: `SOURCE IMPLEMENTED / FOCUSED VALIDATION WORKFLOW INSTALLED / HOSTED VALIDATION PENDING / RUNTIME ACTIVATION NOT CLAIMED`

## Source of truth

This file is the repo-local continuation record for the StegCore GADI reasoning/planning slice required by `StegVerse-Labs/StegCore#190`.

Inherited authority and contracts:
- `MANIFOLD_GOVERNANCE_MIRROR_HANDOFF.md`
- `StegVerse-Labs/.github/docs/GOVERNED_MULTILANE_MANIFOLD_ACTIVATION_MIRROR_HANDOFF.md`
- `StegVerse-Labs/.github/docs/GADI_MIRROR_HANDOFF.md`
- `StegVerse-Labs/StegOS/docs/GADI_STEGOS_MIRROR_HANDOFF.md`
- `StegVerse-Labs/StegOS/stegos/gadi_contracts.py`

Canonical runtime governance remains StegCore/StegGate/InTr. Credential authority remains TV/TVC. Wallet signing/broadcast remains USER_ONLY.

## Implemented source

Developed files on `gadi-stegcore-001`:
- `src/stegcore/gadi_defense_planner.py`
- `tests/test_gadi_defense_planner.py`
- `.github/workflows/gadi-stegcore.yml`
- `GADI_STEGCORE_MIRROR_HANDOFF.md`

The planner:
1. consumes subject-bound `GADI-001` threat observations;
2. enforces task/COSV, non-authorizing observation, subject binding, and freshness checks;
3. retains evidence references and material unknowns;
4. requires credible evidence before producing an intervention plan;
5. routes material uncertainty to review instead of actuation planning;
6. filters capabilities to TV/TVC-governed, preauthorization-required, production-eligible, in-scope surfaces;
7. deterministically ranks competing candidates by destructiveness/reversibility;
8. emits `stegos.defensive_intervention_request.v1` with admission `PENDING`, model authority `NONE`, and `ADMISSION_REQUIRED_BEFORE_ACTUATION`;
9. fails closed when no qualifying in-scope capability exists;
10. performs no external action, admission, credential issuance, worker claim, or runtime state mutation.

## Acceptance coverage installed

Focused tests cover:
- positive credible-threat path;
- deterministic least-destructive selection;
- ambiguous/material-uncertainty review path;
- stale observation fail-closed path;
- over-scoped/wrong-target capability fail-closed path;
- low-confidence non-intervention path;
- non-admitted output remaining non-authorizing;
- provenance retention and permutation-stable request correlation.

Hosted validation workflow: `.github/workflows/gadi-stegcore.yml`.

Current hosted validation evidence: `PENDING` — no qualifying workflow run has yet been observed for the latest branch head. Merge is therefore not yet claimed despite GitHub reporting PR #191 mergeable.

## Authority boundary

This task may not:
- admit or execute an intervention itself;
- mint credentials or runtime authority;
- create a second StegGate evaluator, worker registry, heartbeat, scheduler, claim/fence mechanism, or runtime-truth source;
- convert model output, confidence, urgency, or threat severity into authorization;
- target unauthorized third-party systems.

The output is planning evidence only until admitted by existing governance authority and bound to a pre-authorized defensive capability.

## Completion boundary

Source build is materially complete, but `GADI-STEGCORE-001` is not release-complete until the focused hosted validation passes and the exact validated head is merged through repository controls. It does not prove GADI runtime activation and does not satisfy the parent manifold activation by itself.

After an exact validated merge, upstream `.github` must re-observe the child disposition and continue canonical WorkerCoordinator/resident traversal. Any release/tag decision remains blocked until owning-repository release criteria are met.

## Remaining evidence / modules

Destination `StegVerse-Labs/StegCore`:
- hosted focused validation result for PR #191 exact head;
- exact validated merge evidence;
- issue #190 closure after merge;
- later runtime/manifold consumption evidence through existing StegGate/InTr authority.

Destination `StegVerse-Labs/.github` after merge:
- updated GADI child disposition in the governed manifold lineage;
- WorkerCoordinator/resident claim/fence/traversal evidence for the umbrella activation;
- authentic multi-lane receipts and reconciliation evidence.

## Propagation

No tag/release is warranted from source existence alone. If/when an owning release is actually tagged, create propagation verification for:
- `StegVerse-Labs/Site`
- `GCAT-BCAT-Engine/Publisher`
- `admissibility-wiki`
- `stegguardian-wiki`
