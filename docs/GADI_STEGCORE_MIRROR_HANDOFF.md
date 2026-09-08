# GADI StegCore Mirror Handoff

Status: ACTIVE / STEGOS_CONTRACT_ALIGNED / SOURCE_VALIDATION_PASS
Repository: `StegVerse-Labs/StegCore`
Canonical task: `GADI-001`
Parent handoff: `StegVerse-Labs/.github/docs/GADI_MIRROR_HANDOFF.md`
COSV: `10100000100000`
Branch: `gadi-001-stegcore-threat-reasoning`
PR: `StegVerse-Labs/StegCore#192`

## Purpose

Implement the StegCore reasoning surface for Governed Autonomous Defensive Intervention (GADI): consume `AUTONOMOUS_THREAT_OBSERVATION`, correlate evidence into a threat state, preserve uncertainty and semantic qualifiers, generate bounded `DEFENSIVE_INTERVENTION_REQUEST` candidates, compare candidate interventions using least-destructive-effective semantics, and hand candidates to the existing canonical StegGate/InTr admissibility path without creating a parallel authority.

## Preflight

- Canonical GADI handoff resolved before mutation.
- Existing StegCore authority boundary inspected: StegCore/StegGate remains the canonical commit-time admissibility runtime.
- No GADI-specific StegCore handoff existed on `main`; creating this file was therefore the first mutation for this bounded owner.
- README impact: **required** because GADI adds a new repository behavior surface (threat correlation and intervention candidate generation) even though it does not add execution or credential authority. README is updated in the same change set.
- Existing authority boundaries remain unchanged: no credential minting, no durable receipt minting, no external execution, no parallel policy evaluator.

## Core invariant

StegCore may derive a threat assessment and propose a defensive transition, but it does not grant authority to execute that transition. Every consequential action candidate must still be submitted to the canonical StegGate/InTr governance path and separately bind to an available pre-authorized capability.

## Semantic-integrity defensive posture

External AI observations can be dangerous even when downstream execution uses valid permissions if the originating meaning is materially distorted before governance. GADI therefore preserves semantic qualifiers as evidence rather than silently strengthening them.

Examples that must remain distinguishable:

- `may` must not silently become `is`;
- suspicion must not silently become fact;
- analysis must not silently become instruction;
- recommendation must not silently become authorization;
- bounded scope must not silently broaden;
- inferred motive must not silently become asserted motive.

The reasoning layer records semantic-integrity state as observation evidence. A semantic-integrity finding alone does not elevate the threat state and does not make an intervention eligible; it can only contribute observable evidence for correlation and later reconstruction.

## Installed implementation

- `src/stegcore/gadi.py`
  - canonical StegOS `stegos.autonomous_threat_observation.v1` input model;
  - canonical StegOS `stegos.governed_intervention_capability.v1` capability model;
  - canonical StegOS `stegos.defensive_intervention_request.v1` output model;
  - typed GADI threat states;
  - freshness-aware observation correlation;
  - subject-binding checks;
  - uncertainty preservation;
  - semantic-integrity assessment;
  - least-destructive-effective capability selection;
  - PENDING InTr admission request generation;
  - fail-closed behavior for expired, materially uncertain, unbound, or disproving evidence.
- `tests/test_gadi.py`
  - StegOS schema constant/authority-boundary assertions;
  - qualifier preservation;
  - material semantic drift detection;
  - proof that semantic drift alone does not elevate threat state;
  - expired observation rejection;
  - uncertainty and disproving-evidence blocking;
  - least-destructive effective capability selection;
  - expired/wrong-mode capability exclusion;
  - PENDING admission semantics and no model-output authority;
  - timezone-aware deterministic correlation requirement.
- `.github/workflows/gadi-contract-validation.yml`
  - bounded Python 3.11 validation lane for the GADI source/tests;
  - compile check plus `tests/test_gadi.py`;
  - branch-native push trigger plus PR/manual validation entry points.
- `README.md`
  - documents GADI reasoning boundary and explicit non-authority semantics.

## Contract alignment evidence

The implementation was reconciled against the current canonical StegOS schemas on 2026-09-08:

- `StegVerse-Labs/StegOS/schemas/autonomous-threat-observation.v1.schema.json`
- `StegVerse-Labs/StegOS/schemas/defensive-intervention-request.v1.schema.json`
- `StegVerse-Labs/StegOS/schemas/governed-intervention-capability.v1.schema.json`

The first StegCore draft used local shorthand field shapes. That mismatch was identified before merge and replaced with models that preserve the canonical StegOS schema names, task/COSV constants, observation authority effect, TV/TVC capability authority boundary, PENDING InTr admission structure, stop/reassessment semantics, and model-output authority `NONE`.

No runtime activation or external defensive effect is claimed by this source work.

## Acceptance criteria for this bounded owner

1. A valid fresh threat observation can be correlated into a deterministic threat-state assessment. **PASS**
2. Expired, materially uncertain, unbound, or disproving critical evidence cannot produce an intervention-eligible `IMMINENT_HARM` assessment. **PASS**
3. Semantic qualifiers are preserved and material drift is surfaced as evidence without independently elevating threat state. **PASS**
4. Candidate interventions are selected only from fresh, mode-eligible, target-scoped TV/TVC capabilities and choose the least-destructive candidate satisfying the effectiveness threshold. **PASS**
5. Generated intervention requests match the canonical StegOS contract, begin with `PENDING` InTr admission, require reassessment/stop conditions, and preserve `model_output_authority: NONE`. **PASS**
6. Tests demonstrate the above behavior. **PASS**
7. README reflects the added behavior and authority boundary. **PASS**

## Validation evidence

GitHub Actions run `34277838533` on branch commit `e113962c0016bb9f875b3574035f73c16f106bae` completed successfully:

- checkout: PASS
- Python 3.11 setup: PASS
- editable StegCore install: PASS
- `python -m pytest -q tests/test_gadi.py`: PASS
- `python -m py_compile src/stegcore/gadi.py`: PASS
- overall job `validate-gadi-contracts`: SUCCESS

This proves the bounded StegCore source/tests compile and pass their GADI contract assertions. It does **not** prove runtime InTr admission, TV/TVC runtime binding, external safe-state effect, adaptive reassessment, Continuity reconstruction, or GADI activation.

## Current bounded-owner disposition

StegCore source implementation for the current GADI reasoning scope is validation-complete on PR #192 and mergeable according to the current PR state. Merge/release is still distinct from runtime activation and cross-repository GADI completion.

## Remaining ecosystem work after StegCore

- StegOS contract validation receipt / existing repository validation path -> `StegVerse-Labs/StegOS`
- Governed Intervention Capability Registry runtime data and TV/TVC bindings -> `StegVerse-Labs/StegOS`, `StegVerse-Labs/TV`, `StegVerse-Labs/TVC`
- Defensive capability custody/runtime bindings -> `StegVerse-Labs/TV`, `StegVerse-Labs/TVC`
- GADI resident executor/reassessment loop -> `StegVerse-002/micro-node-runtime`
- Intervention receipt/reconstruction package -> `StegVerse-Labs/Continuity`
- External-threat/HIL readiness/proof surface -> `StegVerse-Labs/Site`
- Cross-repo closed-loop simulation and activation evidence -> canonical runtime coordination

## Release propagation

When GADI reaches release/tag readiness, verify pertinent semantics are propagated/applied to:

- `StegVerse-Labs/Site`
- `GCAT-BCAT-Engine/Publisher`
- `admissibility-wiki`
- `stegguardian-wiki`

## Continuation

Resolve this handoff, the parent `.github` GADI handoff, PR #192, current workflow/check state, canonical StegOS schemas, and existing StegCore authority contracts before any further mutation.
